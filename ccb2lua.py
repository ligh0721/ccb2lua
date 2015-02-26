#!/usr/bin/env python
# Created by jing.liu on 15-01-22

import cocosbuilder
from cocosbuilder import safevalue, safevaluex
import mako.template, mako.exceptions
from mako.exceptions import RichTraceback
import sys
import os
import time


def onParseNode(node, **argvs):
	displayName             = safevalue(node, 'displayName')
	baseClass               = safevalue(node, 'baseClass')
	customClass             = safevalue(node, 'customClass')
	memberVarAssignmentType = safevalue(node, 'memberVarAssignmentType')
	memberVarAssignmentName = safevalue(node, 'memberVarAssignmentName')
	animatedProperties      = safevalue(node, 'animatedProperties')
	properties              = safevalue(node, 'properties')

	level                   = argvs['__level__']
	_tplVars                = argvs['tplVars']
	tplList                 = argvs['tplList']

	_lists                  = safevaluex(_tplVars, 'lists', dict())
	
	# set ${className}
	safevaluex(_tplVars, 'className', memberVarAssignmentName or '__UnnamedClass')

	if level == 0:
		return

	curListLevel = safevaluex(tplList, 'curListLevel', -1)
	if curListLevel >= 0 and level <= curListLevel:
		# exit this list mode
		curListLevel = -1
		tplList['curListLevel'] = curListLevel
	

	if (memberVarAssignmentName.find('m_list') == 0 or memberVarAssignmentName.find('list') == 0) and curListLevel < 0:
		# enter new list mode
		tplList['curListLevel'] = level
		tplList['curListName'] = memberVarAssignmentName
		safevaluex(_lists, memberVarAssignmentName, list((dict(),)))  # $lists[listName] = templates

	else:
		if curListLevel >= 0:
			# in list mode
			# _lists = {'listName': [{'name': itemTplName, 'selectors': {selector, ...}, 'vars': {'varName': {'type': 'varType', 'tag': 'varTag'}, ...}}, ...], ...}
			curListName = tplList['curListName']
			_curListTpl = _lists[curListName][0]  # only support single template
			if level == curListLevel + 1:
				# template name
				_curListTpl['name'] = memberVarAssignmentName or '__UnnamedTemplate'

			elif level == curListLevel + 2:
				# template children, set ${listTplVars}
				_curListTplVars = safevaluex(_curListTpl, 'vars', dict())

				if not memberVarAssignmentName:
					memberVarAssignmentName = '__UnnamedVar'

				if memberVarAssignmentName in _curListTplVars:
					memberVarAssignmentName = autonamevar(_curListTplVars, memberVarAssignmentName)
				
				_curListTplVar  = safevaluex(_curListTplVars, memberVarAssignmentName, dict())
				_curListTplVar['type'] = customClass or baseClass or 'CCNode'
				#_curListTplVar['tag'] = '<UndefinedTag>'
				#_curListTplVar['sortKey'] = len(_curListTplVars)

		else:
			# not in list mode
			if memberVarAssignmentType == 2 and memberVarAssignmentName:  # owner vars
				# set ${vars}
				_vars = safevaluex(_tplVars, 'vars', dict())
				
				if not memberVarAssignmentName:
					memberVarAssignmentName = '__UnnamedVar'

				if memberVarAssignmentName in _vars:
					memberVarAssignmentName = autonamevar(_vars, memberVarAssignmentName)
				
				_vars[memberVarAssignmentName] = customClass or baseClass or 'CCNode'  # set var
				

		if properties != None:
			for p in properties:
				pn = safevalue(p, 'name')
				pt = safevalue(p, 'type')
				pv = safevalue(p, 'value')
				if (pn == 'block' and pt == 'Block') or (pn == 'ccControl' and pt == 'BlockCCControl'):
					selector = pv[0]
					selectortype = pv[1]

					if curListLevel >= 0 and level == curListLevel + 2:
						# in list mode
						curListName          = tplList['curListName']
						_curListTpl          = _lists[curListName][0]  # only support single template
						_curListTplVars      = _curListTpl['vars']
						_curListTplSelectors = safevaluex(_curListTpl, 'selectors', set())
						_curListTplSelectors.add(selector)
						_curListTplVars[memberVarAssignmentName]['selector'] = selector

					elif curListLevel < 0 and selectortype == 2:  # owner
						# set ${selectors}
						_selectors = safevaluex(_tplVars, 'selectors', set())
						_selectors.add(selector)
						break

				elif pn == 'tag' and pt == 'Integer' and curListLevel > 0 and level == curListLevel + 2:
					curListName     = tplList['curListName']
					_curListTpl     = _lists[curListName][0]
					_curListTplVars = safevaluex(_curListTpl, 'vars', dict())
					_curListTplVar  = safevaluex(_curListTplVars, memberVarAssignmentName, dict())
					_curListTplVar['tag'] = pv



def onParseSeq(seq, **argvs):
	autoPlay        = safevalue(seq, 'autoPlay')
	callbackChannel = safevalue(seq, 'callbackChannel')

	keyframes       = safevalue(callbackChannel, 'keyframes')

	_tplVars        = safevalue(argvs, 'tplVars')

	for kf in keyframes:
		kftype      = safevalue(kf, 'type')

		if kftype == 10:
			kfvalue = safevalue(kf, 'value')
			v1      = kfvalue[0]
			v2      = kfvalue[1]
			if v2 == 2:
				# set ${callbacks}
				_callbacks = safevaluex(_tplVars, 'callbacks', set())
				_callbacks.add(v1)


def autoname(path):
	suffix = 2
	title, ext = os.path.splitext(path)
	while os.path.exists(path):
		path = title + '_(' + str(suffix) + ')' + ext
		suffix += 1

	return path


def autonamevar(d, name):
	while name in d:
		res = name.rsplit('_', 1)
		if len(res) == 2 and res[1].isdigit():
			name = res[0] + '_' + str(int(res[1]) + 1)
		else:
			name = name + '_2'

	return name


def render(tplFile, outFile, **tplVars):
	#print tplVars
	t = mako.template.Template(filename = tplFile)
	try:
		output = t.render(**tplVars)
	except:
		print 'Traceback:'
		tb = RichTraceback()
		for filename, lineno, func, line in tb.traceback:
			print '  File "%s", line %d, in %s' % (filename, lineno, func)
			print '    %s\n' % line
		print '%s: %s' % (str(tb.error.__class__.__name__), tb.error)
		exit(0)

	f = open(outFile, 'w')
	f.write(output)
	f.close()


def usage():
	me = sys.argv[0]
	print 'usage:   ' + me + ' <PACKAGE_NAME> <CCB_FILE>'
	print 'example: ' + me + ' warehouse /Users/jing.liu/.../UI_Warehouse.ccb'


def main():
	if len(sys.argv) < 3:
		usage()
		exit(0)


	tpl = 'templates/ListPanel.tpl'
	pkg = sys.argv[1]
	ccb = sys.argv[2]

	
	tplVars = dict()

	tplVars['author']      = os.getlogin()
	tplVars['date']        = time.strftime("%y-%m-%d", time.localtime())
	tplVars['luaPkgName']  = pkg
	tplVars['resDescName'] = os.path.basename(ccb) + 'i'
	
	#tplVars['className']
	tplVars['vars']        = dict()
	tplVars['selectors']   = set()
	tplVars['callbacks']   = set()
	tplVars['lists']       = dict()

	tplList = dict()

	parser = cocosbuilder.CCBParser(ccb)
	parser.parseCCNodes(onParseNode, tplVars = tplVars, tplList = tplList)
	parser.parseSeqs(onParseSeq, tplVars = tplVars)

	if not os.path.exists(pkg):
		os.mkdir(pkg)

	save = pkg + '/' + tplVars['className'] + '.lua'
	save = autoname(save)

	render(tpl, save, **tplVars)


	for listName, listTpls in tplVars['lists'].iteritems():
		listTpl     = listTpls[0]
		listTplName = listTpl['name']
		save = pkg + '/ItemRendererFor' + listTplName + '.lua'
		save = autoname(save)
		tplVarsForListTpl = dict()
		tplVarsForListTpl['author'] = tplVars['author']
		tplVarsForListTpl['date']   = tplVars['date']
		tplVarsForListTpl['tpl']    = listTpl
		render('templates/ListItemRenderer.tpl', save, **tplVarsForListTpl)


if __name__ == '__main__':
	main()
