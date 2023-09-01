import sublime
import sublime_plugin
import os
import re
import logging
import sys
import subprocess

hex_rgb = ''

hex_rgba = ''

rgb_functional = ''

rgba_functopnal = ''

hsl_a = ''
hsl_a += '(hsl\()'
hsl_a += '([0-3][0-9][0-9]|[0-9]?[0-9])'
hsl_a += '(, ?)'
hsl_a += '(100|\d{1,2})'
hsl_a += '(%, ?)'
hsl_a += '(100|\d{1,2})'
hsl_a += '(%\))'

hsl_functional_notag = ''

hsla_functional = ''

hwb_functional = ''

no_type_3 = ''
no_type_3 += '(\()'
no_type_3 += '([0-2][0-5]{2}|\d{1,2})'
no_type_3 += '(\.\d+)?'
no_type_3 += '(, ?)'
no_type_3 += '([0-1]00|\d{1,2})'
no_type_3 += '(\.\d+)?'
no_type_3 += '(\.\d+)?'
no_type_3 += '(, ?)'
no_type_3 += '([0-1]00|\d{1,2})'
no_type_3 += '(\.\d+)?'
no_type_3 += '(\.\d+)?'
no_type_3 += '\)'

no_type_4 = ''


class viewEventListenter(sublime_plugin.ViewEventListener):

	def on_activated(self):

		path = get_mod_path()

		if os.path.isfile(path) == False:
			
			make_mod(path)

		extracts = []
		regions = self.view.find_all(hsl_a, 0, '[$2, $4, $6]', extracts)

		update(extracts, regions, self.view)


	def on_hover(self, pt, zone):

		line = self.view.line(pt)
		substr = self.view.substr(line)

		regex = re.compile(hsl_a)
		matches = regex.findall(substr)

		if len(matches) > 0:

			html = "<a href='subl:popup_handler {\"view\": "
			html += "{0}, \"pt\": {1}".format(self.view.id(), pt)
			html += "}'>Change Color</a>"

			# show popup at mouse location
			self.view.show_popup(html, 0, pt)


class textChangeListener(sublime_plugin.TextChangeListener):

	def on_text_changed_async(self, changes):

		view = sublime.active_window().active_view()
		region = view.sel()
		line = view.line(region[0])

		extracts, regions = search_line(view, line)
		# print(extracts, regions)
		update(extracts, regions, view)


class popupHandlerCommand(sublime_plugin.TextCommand):

	def run(self, edit, view, pt):

		line = sublime.View(view).line(pt)

		extracts, regions = search_line(sublime.View(view), line)

		iterations = len(extracts)

		if iterations == 1:

			color_in = extracts[0]

			args = ['python', 'C:\\Users\\lucas\\Dropbox\\git\\please_colors\\main.py', '-s', color_in]

			proc = subprocess.check_output(args, universal_newlines=True)
			proc = proc.split('\n')

			new_extracts = ['{0}, {1}, {2}'.format(proc[0], proc[1], proc[2])]
			color_phrase = 'hsl({0}, {1}%, {2}%)'.format(proc[0], proc[1], proc[2])
			print(color_phrase)
			print(regions)
			# print(view)
			# print(sublime.View(view))
			sublime.View(view).replace(edit, regions[0], color_phrase)
			# update(new_extracts, regions, sublime.View(view))


def make_mod():

	with open(get_mod_path(), 'w') as mod:
		
		boiler = '{\n\t"variables":\n\t{\n\t},'
		boiler += '\n\t"globals":\n\t{\n\t},'
		boiler += '\n\t"rules":\n\t[\n\t]\n}'
		mod.write(boiler)


def update(extracts, regions, view):
	# print(extracts, regions)
	iterations = len(extracts)

	if iterations > 0:

		for i in range(iterations):
			extracts[i] = eval(extracts[i])

		packet = make_packet('hsl', extracts, regions, iterations)
		
		update_scope(packet, view)
		update_mod(packet)


def make_packet(type, extracts, regions, instances):

	packet = {
		'instances': instances,
		'type': type,
		'colors': [],
		'scopes': [],
		'rules': [],
		'regions': [],
		'vals': []
	}

	for i in range(instances):

		extract = extracts[i]
		region = regions[i]


		color = '{0}({1}, {2}%, {3}%)'.format(packet['type'], extract[0], extract[1], extract[2])

		scope = 'hsl_{0}'.format(extract)

		rule = '\n\t\t{{\n\t\t\t"scope": "{0}'.format(scope)
		rule += '",\n\t\t\t"background": "{0}'.format(color)
		rule += '"\n\t\t},'

		packet['rules'].append(rule)
		packet['colors'].append(color)
		packet['scopes'].append(scope)
		packet['regions'].append(region)

	return(packet)


def search_line(view, line):

	substr = view.substr(line)

	regex = re.compile(hsl_a)
	matches = regex.findall(substr)
	# print(matches)

	extracts = []
	regions = []

	for match in matches:

		extract_a = '{0}{1}{2}{3}{4}{5}{6}'.format(match[0], match[1], match[2], match[3], match[4], match[5], match[6])
		extract_b = '[{0}, {1}, {2}]'.format(match[1], match[3], match[5])
		extracts.append(extract_b)

		region_a = substr.find(extract_a) + line.a
		region_b = region_a + len(extract_a)
		region = sublime.Region(region_a, region_b)
		regions.append(region)

	# print(regions)
	return(extracts, regions)


def update_scope(packet, view):

	for i in range(packet['instances']):

		scope = packet['scopes'][i]
		matches = view.get_regions(scope)

		if len(matches) == 0:

			view.add_regions(scope, [packet['regions'][i]], scope)


def update_mod(packet):

	content = get_mod_contents()[:-len('\n\t]\n}')]

	for i in range(packet['instances']):

		idx = content.find(packet['scopes'][i])

		if idx == -1:

			content += packet['rules'][i]

	if packet['instances'] > 0:

		content += '\n\t]\n}'

		with open(get_mod_path(), 'w') as mod:

			mod.write(content)


def get_mod_path():

	path = '{0}\\please_colors_highlight\\{1}'.format(
		sublime.packages_path(),
		sublime.ui_info()['color_scheme']['value'])

	return(path)


def get_mod_contents():

	with open(get_mod_path(), 'r') as mod:

		contents = mod.read()
		return(contents)


