import sublime
import sublime_plugin
import os
import re
import logging
import sys
import subprocess
import please_colors_highlight.regexes as regexes


class viewEventListenter(sublime_plugin.ViewEventListener):

	def on_activated(self):

		path = get_mod_path()

		if os.path.isfile(path) == False:

			make_mod(path)

		phrases_hsl = []
		regions_hsl = self.view.find_all(regexes.hsl_a, 0, '$0', phrases_hsl)

		if len(phrases_hsl) > 0:

			data_hsl = make_data(phrases_hsl)

			scopes_hsl = make_scopes(data_hsl)

			update_scope(phrases_hsl, scopes_hsl, regions_hsl, self.view)

			update_mod(phrases_hsl, scopes_hsl)

		phrases_hex = []
		phrases_hex = self.view.find_all(regexes.hex_a, 0, '$0', phrases_hex)

		print(phrases_hex)


	def on_hover(self, pt, zone):

		line = self.view.line(pt)

		substr = self.view.substr(line)

		phrases, regions = search_line(line, self.view)

		if len(phrases) == 1:

			datum = make_data(phrases)[0]

			region = str(regions[0])

			args = {
				"datum": datum,
				"region": region,
				"view_id": self.view.id()
			}

			cmd = sublime.command_url('popup_handler', args)

			html = '<a href=\"{0}\">Edit Color</a>'.format(cmd)
			
			self.view.show_popup(html, 0, pt)


class textChangeListener(sublime_plugin.TextChangeListener):

	def on_text_changed_async(self, changes):

		view = sublime.active_window().active_view()

		region = view.sel()

		line = view.line(region[0])

		phrases, regions = search_line(line, view)

		if len(phrases) > 0:

			data = make_data(phrases)

			scopes = make_scopes(data)

			update_scope(phrases, scopes, regions, view)

			update_mod(phrases, scopes)


class popupHandlerCommand(sublime_plugin.TextCommand):

	def run(self, edit, datum, region, view_id):

		args = ['pythonw', 'C:\\Users\\lucas\\Dropbox\\git\\please_colors\\main.py', str(datum)]

		proc = subprocess.check_output(args, universal_newlines=True)
		# proc = proc.split('\n')

		# print(proc)

		try:
	
			datum[1] = eval(proc)

			for i in range(len(datum[1])):

				datum[1][i] = round(datum[1][i], 3)

			scopes = make_scopes([datum])

			phrase = '{0}({1}, {2}%, {3}%)'.format(datum[0], datum[1][0], datum[1][1], datum[1][2])

			print(phrase)

			region = eval(region)

			region_a = sublime.Region(region[0], region[1])

			view = sublime.View(view_id)

			view.replace(edit, region_a, phrase)

			region_b = sublime.Region(region[0], region[0] + len(phrase))

			update_scope([phrase], scopes, [region_b], view)

			update_mod([phrase], scopes)

		except:

			return

def make_rules(phrases, scopes):

	rules = []

	for i in range(len(phrases)):

		rule = '\n\t\t{{\n\t\t\t\"scope\": \"{0}'.format(scopes[i])
		rule += '\",\n\t\t\t\"background\": \"{0}'.format(phrases[i])
		rule += '\"\n\t\t},'

		rules.append(rule)

	return(rules)


def make_data(phrases):

	data = []

	for phrase in phrases:

		datum = ['', []]

		phrase = phrase.split('(')

		color_type = phrase[0]

		datum[0] = color_type

		nums = phrase[1]
		nums = nums.replace(' ', '')
		nums = nums.replace('%', '')
		nums = nums.replace(')', '')
		nums = nums.split(',')

		for num in nums:

			datum[1].append(float(num))

		data.append(datum)

	return(data)


def make_scopes(data):

	scopes = []

	for datum in data:

		scope = datum[0]

		for num in datum[1]:

			scope += '_' + str(num)

		scopes.append(scope)

	return scopes


def update_scope(phrases, scopes, regions, view):

	for i in range(len(phrases)):

		existing_regions = view.get_regions(scopes[i])

		if len(existing_regions) == 0:

			view.add_regions(scopes[i], [regions[i]], scopes[i])


def update_mod(phrases, scopes):

	content = get_mod_content()[:-len('\n\t]\n}')]

	rules = make_rules(phrases, scopes)

	for i in range(len(phrases)):

		idx = content.find(phrases[i])

		if idx == -1:

			content += rules[i]

	content += '\n\t]\n}'

	with open(get_mod_path(), 'w') as mod:

		mod.write(content)


def search_line(line, view):

	substr = view.substr(line)

	regex = re.compile(regexes.hsl_a)

	instances = regex.findall(substr)

	phrases = []
	regions = []

	for i in instances:

		phrase = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}'.format(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10])

		region_a = substr.find(phrase) + line.a
		region_b = region_a + len(phrase)

		region = sublime.Region(region_a, region_b)
		
		phrases.append(phrase)
		regions.append(region)

	return(phrases, regions)


def make_mod():

	with open(get_mod_path(), 'w') as mod:
		
		boiler = '{\n\t"variables":\n\t{\n\t},'
		boiler += '\n\t"globals":\n\t{\n\t},'
		boiler += '\n\t"rules":\n\t[\n\t]\n}'
		mod.write(boiler)

		print('New mod file created.')


def get_mod_path():

	path = '{0}\\please_colors_highlight\\{1}'.format(
		sublime.packages_path(),
		sublime.ui_info()['color_scheme']['value'])

	return(path)


def get_mod_content():

	with open(get_mod_path(), 'r') as mod:

		contents = mod.read()
		return(contents)


