import json
import os
import logging

from widgets_elements.vispyNodeLib import Node, Socket, Edge


def _socket_value(socket):
	try:
		# text input
		if getattr(socket, 'type', None) and getattr(socket.type, 'shape', None) == 'TextInput':
			return socket.get_text_value()
		# eval/dropdown input
		if getattr(socket, 'type', None) and getattr(socket.type, 'shape', None) == 'EvalInput':
			return socket.get_eval_value()
	except Exception:
		logging.exception('Error reading socket value')
	return None


def save_scene_to_file(scene, path):
	"""Serialize the given QGraphicsScene to a JSON file.

	The format contains a `nodes` list and an `edges` list. Nodes include
	id, type, title, position, inputs and outputs. Inputs that are text
	or eval widgets will include their current value.
	"""
	data = {"nodes": [], "edges": []}

	# Collect nodes first
	for item in list(scene.items()):
		try:
			if isinstance(item, Node):
				node = item
				node_id = getattr(getattr(node, 'data', None), 'id', None)
				node_type = getattr(getattr(node, 'data', None), 'node_type', getattr(node, 'title', None))
				node_dict = {
					'id': node_id,
					'type': node_type,
					'title': getattr(node, 'title', ''),
					'pos': [node.pos().x(), node.pos().y()],
					'inputs': [],
					'outputs': []
				}

				# sockets are stored on the node as a list
				for idx, sock in enumerate(getattr(node, 'sockets', []) or []):
					try:
						sock_info = {
							'name': getattr(sock, 'name', ''),
							'index': idx,
							'type': getattr(getattr(sock, 'type', None), 'name', None),
							'shape': getattr(getattr(sock, 'type', None), 'shape', None)
						}
						if sock.pos().x() <= 0:
							# input socket
							sock_info['value'] = _socket_value(sock)
							node_dict['inputs'].append(sock_info)
						else:
							node_dict['outputs'].append(sock_info)
					except Exception:
						logging.exception('Error serializing socket')

				data['nodes'].append(node_dict)
		except Exception:
			logging.exception('Error serializing node')

	# Collect edges (only fully connected edges saved)
	for item in list(scene.items()):
		try:
			if isinstance(item, Edge):
				edge = item
				# only save edges connected to two sockets
				if not isinstance(edge.start, Socket) or not isinstance(edge.end, Socket):
					continue

				# find parent nodes for sockets
				start_parent = getattr(edge.start, 'parentItem', lambda: None)()
				end_parent = getattr(edge.end, 'parentItem', lambda: None)()

				start_node_id = getattr(getattr(start_parent, 'data', None), 'id', None)
				end_node_id = getattr(getattr(end_parent, 'data', None), 'id', None)

				# socket indices within their parent node
				start_index = None
				end_index = None
				try:
					if hasattr(start_parent, 'sockets'):
						for i, s in enumerate(start_parent.sockets):
							if s is edge.start:
								start_index = i
								break
					if hasattr(end_parent, 'sockets'):
						for i, s in enumerate(end_parent.sockets):
							if s is edge.end:
								end_index = i
								break
				except Exception:
					logging.exception('Error locating socket index')

				edge_dict = {
					'start_node_id': start_node_id,
					'start_socket_index': start_index,
					'end_node_id': end_node_id,
					'end_socket_index': end_index,
					'type': getattr(getattr(edge, 'type', None), 'name', None)
				}
				data['edges'].append(edge_dict)
		except Exception:
			logging.exception('Error serializing edge')

	# Ensure directory exists
	try:
		os.makedirs(os.path.dirname(path), exist_ok=True)
	except Exception:
		pass

	# Write JSON to file
	with open(path, 'w', encoding='utf-8') as f:
		json.dump(data, f, indent=2)


def save_scene_via_dialog(parent_window, scene):
	"""Convenience: show a Save dialog and save the scene if a path chosen."""
	from PySide6.QtWidgets import QFileDialog, QMessageBox

	path, _ = QFileDialog.getSaveFileName(parent_window, 'Save File', '', 'Vispy Files (*.vp *.json);;All Files (*)')
	if not path:
		return False
	try:
		save_scene_to_file(scene, path)
		try:
			QMessageBox.information(parent_window, 'Save', f'Saved to: {path}')
		except Exception:
			pass
		return True
	except Exception:
		logging.exception('Failed to save scene')
		try:
			QMessageBox.critical(parent_window, 'Save Error', 'Failed to save file. See logs.')
		except Exception:
			pass
		return False


def load_scene_from_file(scene, path):
	"""Load a scene JSON file and reconstruct nodes and edges in the provided QGraphicsScene.

	This will remove existing Node and Edge items from the scene before loading.
	"""
	try:
		with open(path, 'r', encoding='utf-8') as f:
			data = json.load(f)
	except Exception:
		logging.exception('Failed to read scene file')
		raise

	# remove existing Node and Edge items
	try:
		items = list(scene.items())
		for it in items:
			try:
				if isinstance(it, Edge) or isinstance(it, Node):
					scene.removeItem(it)
			except Exception:
				pass
	except Exception:
		logging.exception('Error clearing scene')

	# mapping from saved node id to Node instance
	node_map = {}

	# helper to find type profile by name if needed
	def _type_from_name(name):
		try:
			from types_classes.vispyDataTypes import types as _types_module
			for attr in dir(_types_module):
				val = getattr(_types_module, attr)
				if getattr(val, 'name', None) == name:
					return val
		except Exception:
			pass
		return None

	# Recreate nodes
	for node_entry in data.get('nodes', []):
		try:
			node_type = node_entry.get('type')
			# try to create NodeData using node_library makers when available
			from types_classes import node_library as nl
			node_data = None
			# find a maker that creates this type
			for attr in dir(nl):
				if attr.startswith('make_') and attr.endswith('_node'):
					try:
						func = getattr(nl, attr)
						nd = func()
						if getattr(nd, 'node_type', None) == node_type:
							node_data = nd
							break
					except Exception:
						continue

			# fallback: construct a minimal NodeData-like object
			if node_data is None:
				from types_classes.node_data import NodeData
				node_data = NodeData(node_type=node_type)

			# override id if present in file
			sid = node_entry.get('id')
			if sid and hasattr(node_data, 'id'):
				try:
					node_data.id = sid
				except Exception:
					pass

			# create Node
			from widgets_elements.vispyNodeLib import Node as NodeClass
			node = NodeClass(node_data)
			node.title = node_entry.get('title', node.title)
			pos = node_entry.get('pos', [0, 0])
			try:
				node.setPos(pos[0], pos[1])
			except Exception:
				pass

			scene.addItem(node)
			node_map[node_data.id] = node

			# restore input values for sockets
			inputs = node_entry.get('inputs', [])
			outputs = node_entry.get('outputs', [])

			# sockets on Node are listed inputs then outputs
			for sock_info in inputs:
				try:
					idx = sock_info.get('index')
					if idx is None:
						continue
					sock = node.sockets[idx]
					val = sock_info.get('value')
					if val is not None:
						if getattr(sock, 'type', None) and getattr(sock.type, 'shape', None) == 'TextInput':
							sock.set_text_value(val)
						elif getattr(sock, 'type', None) and getattr(sock.type, 'shape', None) == 'EvalInput':
							sock.set_eval_value(val)
				except Exception:
					logging.exception('Error restoring socket input')

			# outputs currently have no widget values to restore
		except Exception:
			logging.exception('Error recreating node')

	# Recreate edges
	for edge_entry in data.get('edges', []):
		try:
			s_nid = edge_entry.get('start_node_id')
			e_nid = edge_entry.get('end_node_id')
			s_idx = edge_entry.get('start_socket_index')
			e_idx = edge_entry.get('end_socket_index')

			start_node = node_map.get(s_nid)
			end_node = node_map.get(e_nid)
			if not start_node or not end_node:
				continue

			if s_idx is None or e_idx is None:
				continue

			try:
				start_socket = start_node.sockets[s_idx]
				end_socket = end_node.sockets[e_idx]
			except Exception:
				continue

			# determine type profile to pass to Edge constructor; prefer start socket type
			etype = getattr(start_socket, 'type', None) or getattr(end_socket, 'type', None)
			# create Edge
			from widgets_elements.vispyNodeLib import Edge as EdgeClass
			edge = EdgeClass(start_socket, end_socket, etype)
			scene.addItem(edge)
		except Exception:
			logging.exception('Error recreating edge')


def load_scene_via_dialog(parent_window, scene):
	from PySide6.QtWidgets import QFileDialog, QMessageBox
	path, _ = QFileDialog.getOpenFileName(parent_window, 'Open File', '', 'Vispy Files (*.vp *.json);;All Files (*)')
	if not path:
		return False
	try:
		load_scene_from_file(scene, path)
		try:
			QMessageBox.information(parent_window, 'Open', f'Loaded: {path}')
		except Exception:
			pass
		return True
	except Exception:
		logging.exception('Failed to load scene')
		try:
			QMessageBox.critical(parent_window, 'Open Error', 'Failed to load file. See logs.')
		except Exception:
			pass
		return False

