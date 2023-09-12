import os
import re
import sys
import logging
import sublime
import subprocess
import sublime_plugin
import color_utility_sublime_plugin.regexes as regexes
import color_utility_sublime_plugin.cu_format as cu_format


color_types = ['hsl', 'rgb_hex', 'notag_rgb_a']


class viewEventListenter(sublime_plugin.ViewEventListener):

	def on_activated(self):
		path = get_mod_path()
		if os.path.isfile(path) == False:
			make_mod(path)

		for color_type in color_types: 
			regex = eval('regexes.' + color_type)
			phrases = []
			regions = self.view.find_all(regex, 0, '$0', phrases)

			if 0 < len(phrases):
				packet = cu_format.make_packet(color_type, phrases, regions)
				uni_update(packet, self.view)


	def on_hover(self, pt, zone):
		line   = self.view.line(pt)
		substr = self.view.substr(line)

		for color_type in color_types:
			packet = substr_search(color_type, line, substr)

			if len(packet['phrases']) == 1:
				args = {
					"datum": packet['data'][0],
					"region": str(packet['regions'][0]),
					"view_id": self.view.id()
				}

				cmd = sublime.command_url('popup_handler', args)
				html = '<a href=\"{0}\">Edit Color</a>'.format(cmd)
	
				self.view.show_popup(html, 0, pt)
				break


class popupHandlerCommand(sublime_plugin.TextCommand):

	def run(self, edit, datum, region, view_id):
		path = 'C:\\Users\\lucas\\Dropbox\\git\\color_utility\\main.py'
		args = ['pythonw', path, str(datum)]

		proc = subprocess.check_output(args, universal_newlines=True)

		print(proc)
		
		try:
			datum = eval(proc)
			color_type = datum[0]
			vals = datum[1]

			phrase = ''

			if color_type == 'hsl':
				phrase = '{0}({1}, {2}%, {3}%)'.format(color_type, vals[0], vals[1], vals[2])

			elif color_type == 'rgb_hex':
				phrase = '#{0}{1}{2}'.format(vals[0], vals[1], vals[2])

			elif color_type == 'notag_rgb_a':
				r = str(vals[0])
				g = str(vals[1])
				b = str(vals[2])
				if len(r) == 3:
					r += '0'
				if len(g) == 3:
					g += '0'
				if len(b) == 3:
					b += '0'
				phrase = '{0} {1} {2}'.format(r, g, b)
				# print(r, g, b)


			print(phrase)
			if phrase != '':
				view = sublime.View(view_id)
				region = eval(region)
				region_a = sublime.Region(region[0], region[1])
				region_b = sublime.Region(region[0], region[0] + len(phrase))

				packet = cu_format.make_packet(color_type, [phrase], [region_b])

				view.replace(edit, region_a, phrase)

				uni_update(packet, view)
		except:
			return()


class textChangeListener(sublime_plugin.TextChangeListener):

	def on_text_changed_async(self, changes):
		view = sublime.active_window().active_view()

		sel = view.sel()
		line = view.line(sel[0])
		substr = view.substr(line)

		# for color_type in color_types:
		# 	packet = substr_search(color_type, line, substr)

			# if 0 < len(packet['phrases']):
			# 	uni_update(packet, view)
			# 	break


def substr_search(color_type, line, substr):
	regex = re.compile(eval('regexes.' + color_type))
	matches = regex.findall(substr)

	phrases = []
	regions = []

	for m in matches:
		phrase_constructor = eval('cu_format.' + 'phrase_constructor_' + color_type)
		phrase = eval(phrase_constructor)
		phrases.append(phrase)

		region_a = line.a + substr.find(phrase)
		region_b = region_a + len(phrase)
		region = sublime.Region(region_a, region_b)
		regions.append(region)

	packet = cu_format.make_packet(color_type, phrases, regions)
	return(packet)


def uni_update(packet, view):
	rules = cu_format.make_rules(packet)

	mod = get_mod()[:-len('\n\t]\n}')]

	for i in range(len(packet['phrases'])):
		existing_regions = view.get_regions(packet['scopes'][i])

		if len(existing_regions) == 0:
			view.add_regions(packet['scopes'][i], [packet['regions'][i]], packet['scopes'][i])
			idx = mod.find(packet['phrases'][i])

			if idx == -1:
				mod += rules[i]

	with open(get_mod_path(), 'w') as mod_file:
		mod_file.write(mod + '\n\t]\n}')


def make_mod():
	with open(get_mod_path(), 'w') as mod:
		
		boiler = '{\n\t"variables":\n\t{\n\t},'
		boiler += '\n\t"globals":\n\t{\n\t},'
		boiler += '\n\t"rules":\n\t[\n\t]\n}'
		mod.write(boiler)

		print('New mod file created.')


def get_mod_path():
	path = '{0}\\color_utility_sublime_plugin\\{1}'.format(
		sublime.packages_path(),
		sublime.ui_info()['color_scheme']['value'])

	return(path)


def get_mod():
	with open(get_mod_path(), 'r') as mod_file:

		mod = mod_file.read()
		return(mod)


