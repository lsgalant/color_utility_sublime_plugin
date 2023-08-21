import sublime
import sublime_plugin
import os
import re
import logging
import sys
import subprocess

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
			update_scope(packet_b_hsl, view, scheme)
			update_mod(packet_b_hsl, scheme)


	def make_packet_a_hsl(self, view):

			extracts = []
			regions = view.find_all(hsl_exp_a, 0, '$1_$2_$3', extracts)
			packet_a_hsl = (regions, extracts)
			return(packet_a_hsl)


class c_d_text_change_listener(sublime_plugin.TextChangeListener):


	def on_text_changed_async(self, changes):
		
		scheme = sublime.ui_info()['color_scheme']['value']

		window = sublime.active_window()
		view = window.active_view()
		
		# packet_a = self.search_line(view)

		# if len(packet_a[0]) > 0:
			# packet_b = make_packet_b(packet_a)
			# print(packet_b)
			# update_scope(packet_b, view, scheme)
			# update_mod(packet_b, scheme)


	def search_line(self, view):
		sel = view.sel()
		region = sel[0]
		line = view.line(region)

		words = view.substr(line)
		comp = re.compile(r"(\()(.*[0-9])(,)(.*[0-9])(,)(.*[0-9].*)(\))")
		results = comp.findall(str(words))

		packet_a = ([], [])

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

			packet_a = (regions, extracts)

		return(packet_a)


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
		# idx = mod_contents.find(scope)
		# print('p')
		matches = view.get_regions(scope)
		# print(idx)
		if len(matches) == 0:
			print('added_new_scope')
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
		# print(mod_contents)
		with open(mod_path, 'w') as mod_file:
			mod_file.write(mod_contents)


def get_mod_contents(mod_path):

	with open(mod_path, 'r') as mod_file:
		mod_contents = mod_file.read()
		return(mod_contents)


def make_mod_file(mod_path):

	with open(mod_path, 'w') as mod_file:
		boiler = '{\n\t"variables":\n\t{\n\t},\n\t"globals":\n\t{\n\t},\n\t"rules":\n\t[\n\t]\n}'
		mod_file.write(boiler)


class TestCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		args = self.search_selection()

		if args == 'No match':
			print(args)

		else:
			please_colors_path = 'C:\\Users\\lucas\\Dropbox\\git\\please_colors'
			command = 'pythonw ' + please_colors_path + '\\main.py ' + '-' + str(args[0]) + ' -' + str(args[1]) + ' -' + args[2]
			print(command)
			subprocess.Popen(command)
			# view = self.view
			print('Please Colors opened')

	def search_selection(self):

		window = sublime.active_window()
		view = window.active_view()
		sel = view.sel()
		region = sel[0]
		line = view.line(region)
		words = view.substr(line)

		hsl_exp_a = re.compile('(hsl\()([0-3][0-9][0-9]|[0-9]?[0-9])(, ?)(100|\d{1,2})(%, ?)(100|\d{1,2})(%\))')
		instances = hsl_exp_a.findall(str(words))

		if len(instances) > 0:
			
			args = (str(float(instances[0][1] / 360)), str(float(instances[0][3])), str(float(instances[0][5])))
			return(args)

		else:
			return('No match')

		# scope = view.extract_scope(region.a)
		# scope_name = view.scope_name(region.a)
		# print(scope_name)
		# print(region)
		# print(scope)


class ExampleCommand(sublime_plugin.TextCommand):
	
	def run(self, edit):	
		
		self.view.insert(edit, 0, "Hello, World!")
		print('x')