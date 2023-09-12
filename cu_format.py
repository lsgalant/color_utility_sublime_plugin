def make_packet(color_type, phrases, regions):
	packet = {
		"phrases": phrases,
		"backgrounds": [],
		"regions": regions,
		"data": [],
		"scopes": []
	}

	for phrase in phrases:

		scope = color_type
		vals = ''

		if color_type == 'hsl':
			packet['backgrounds'].append(phrase)
			phrase = phrase.split('(')

			vals = phrase[1]
			vals = vals.replace(' ', '')
			vals = vals.replace('%', '')
			vals = vals.replace(')', '')
			vals = vals.split(',')

		elif color_type == 'rgb_hex':
			packet['backgrounds'].append(phrase)
			vals = [phrase[1] + phrase[2], phrase[3] + phrase[4], phrase[5] + phrase[6]]

		elif color_type == 'notag_rgb_a':
			vals = phrase.split(' ')
			background = 'rgb({0}, {1}, {2})'.format(round(float(vals[0]) * 255, 2), round(float(vals[1]) * 255, 2), round(float(vals[2]) * 255, 2))
			packet['backgrounds'].append(background)

		for val in vals:
			scope += '_' + str(val)

		datum = [color_type, vals]

		packet['data'].append(datum)
		packet['scopes'].append(scope)

	return(packet)


def make_rules(packet):
	phrases = packet['phrases']
	backgrounds = packet['backgrounds']
	scopes = packet['scopes']
	rules = []
	
	for i in range(len(phrases)):
		rule = '\n\t\t{{\n\t\t\t\"scope\": \"{0}'.format(scopes[i])
		rule += '\",\n\t\t\t\"background\": \"{0}'.format(backgrounds[i])
		rule += '\"\n\t\t},'

		rules.append(rule)

	return(rules)


phrase_constructor_hsl = 'm[0] + m[1] + m[2] + m[5] + m[6] + m[9] + m[10] + m[13]'

phrase_constructor_rgb_hex = 'm[0] + m[1] + m[2] + m[3]'

phrase_constructor_notag_rgb_a = 'm[0] + m[1] + m[2] + m[3] + m[4]' 

data_constructor_hsl = "'[\\'{0}\\', [{1}, {2}, {3}]]'.format(m[0], m[1], m[4], m[7])"

data_constructor_rgb_hex = "'[\\'rgb_hex\\', [{0}, {1}, {2}]]'.format(m[0], m[1], m[2])"