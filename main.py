import sublime
import sublime_plugin
import os
import re
import logging
import sys

# hex_rgb = ''

# hex_rgba = ''

# rgb_functional = ''

# rgba_functopnal = ''

hsl_exp_a = 'hsl\(([0-3][0-9][0-9]|[0-9]?[0-9]), ?(100|\d{1,2})%, ?(100|\d{1,2})%\)'

hsl_functional_notag = ''

# hsla_functional = ''

# hwb_functional = ''

# no_type_3 = '\(([0-2][0-5]{2}|\d{1,2})(\.\d+)?, ?([0-1]00|\d{1,2})(\.\d+)?(\.\d+)?, ?([0-1]00|\d{1,2})(\.\d+)?(\.\d+)?\)'

# no_type_4 = ''

class c_d_event_listenter(sublime_plugin.ViewEventListener):

	def on_activated(self):

		scheme = sublime.ui_info()['color_scheme']['value']
		mod_path = sublime.packages_path() + '\\please_colors_highlight\\' + scheme

		mod_exists = os.path.isfile(mod_path)

		if mod_exists == False:
			make_mod_file(mod_path)

		window = sublime.active_window()
		view = window.active_view()

		packet_a_hsl = self.make_packet_a_hsl(view)

		if len(packet_a_hsl[0]) > 0:
			packet_b_hsl = make_packet_b_hsl(packet_a_hsl)
			# print(packet_b_hsl)
			update_scope(packet_b_hsl, view, scheme)
			update_scheme_mod(packet_b_hsl, scheme)

	def make_packet_a_hsl(self, view):

			extracts = []
			regions = view.find_all(hsl_exp_a, 0, '$1_$2_$3', extracts)
			packet_a_hsl = (regions, extracts)
			return(packet_a_hsl)

class c_d_text_change_listener(sublime_plugin.TextChangeListener):


	def on_text_changed_async(self, changes):
		current_scheme = sublime.ui_info()['color_scheme']['value']

		active_window = sublime.active_window()
		active_view = active_window.active_view()
		
		# raw_packet = self.search_line(active_view)

		# if len(raw_packet[0]) > 0:
			# data_packet = make_data_packet(raw_packet)
			# print(data_packet)
			# update_scope(data_packet, active_view, current_scheme)
			# update_scheme_mod(data_packet, current_scheme)


	def search_line(self, active_view):
		selection = active_view.sel()
		region = selection[0]
		line = active_view.line(region)

		words = active_view.substr(line)
		comp = re.compile(r"(\()(.*[0-9])(,)(.*[0-9])(,)(.*[0-9].*)(\))")
		results = comp.findall(str(words))

		raw_packet = ([], [])

		if len(results) > 0:
			regions = []
			extracts = []

			for result in results:
				extract = result[1] + result[2] + result[3] + result[4] + result[5]
				extract_pct = result[1] + result[2] + result[3] + '%' + result[4] + result[5] + '%'
				extracts.append(extract_pct)

				region_start = words.find(extract) + line.a
				region_end = region_start + len(extract)
				region = sublime.Region(region_start, region_end)
				regions.append(region)

			raw_packet = (regions, extracts)

		return(raw_packet)


def make_packet_b_hsl(packet_a_hsl):

	regions = packet_a_hsl[0]
	extracts = packet_a_hsl[1]

	colors = []
	scopes = []
	rules = []

	for(region, extract) in zip(regions, extracts):
		color = 'hsl('

		split = extract.split('_')
		split[1] += '%'
		split[2] += '%'

		for x in split:
			color += x + ','

		color = color.rstrip(',')
		color += ')'
		colors.append(color)

		scope = 'hsl_' + extract
		scopes.append(scope)

		rule = '\n\t\t{\n\t\t\t"scope": "' + scope + '",\n\t\t\t"background": "' + color + '"\n\t\t},'
		rules.append(rule)

	packet_b_hsl = (scopes, rules, regions)
	return(packet_b_hsl)


def update_scope(packet_b, view, scheme):

	mod_path = sublime.packages_path() + '\\please_colors_highlight\\' + scheme
	mod_contents = get_mod_contents(mod_path)

	scopes = packet_b[0]
	regions = packet_b[2]

	for(scope, region) in zip(scopes, regions):
		idx = mod_contents.find(scope)

		if idx == -1:
			view.add_regions(scope, [region], scope)


def update_mod(packet_b, scheme):

	mod_path = sublime.packages_path() + '\\please_colors_highlight\\' + scheme
	mod_contents = get_mod_contents(mod_path)
	mod_contents = mod_contents[:-len('\n\t]\n}')]

	scopes = packet_b[0]
	rules = packet_b[1]
	regions = packet_b[2]

	for(scope, rule, region) in zip(scopes, rules, regions):
		idx = mod_contents.find(scope)

		if idx == -1:
			mod_contents += rule

	if len(packet_b) > 0:
		mod_contents += '\n\t]\n}'

		with open(mode_path, 'w') as mod_file:
			mode_file.write(mod_contents)


def get_mod_contents(mod_path):

	with open(mod_path, 'r') as mod_file:
		mod_contents = mod_file.read()
		return(mod_contents)


def make_mod_file(mod_path):

	with open(mod_path, 'w') as mod_file:
		boiler = '{\n\t"variables":\n\t{\n\t},\n\t"globals":\n\t{\n\t},\n\t"rules":\n\t[\n\t]\n}'
		file.write(boiler)


class ExampleCommand(sublime_plugin.TextCommand):
	
	def run(self, edit):	
		
		self.view.insert(edit, 0, "Hello, World!")
		print('x')