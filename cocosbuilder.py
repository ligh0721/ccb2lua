#!/usr/bin/env python
# Created by jing.liu on 15-01-22

import biplist
import sys


def safevalue(d, k, df = None):
		if k in d:
			return d[k]
		else:
			return df


def safevaluex(d, k, df):
		if k in d:
			return d[k]
		else:
			d[k] = df
			return df


class CCBParser:
	def __init__(self, filename):
		self.m_data = biplist.readPlist(filename)


	def parseCCNodes(self, func, **argvs):
		CCBParser.parseNode(self.m_data['nodeGraph'], func, **argvs)


	def parseSeqs(self, func, **argvs):
		seqs = self.m_data['sequences']
		for seq in seqs:
			if func(seq, **argvs) == False:
				return


	@staticmethod
	def parseNode(node, func, **argvs):	
		# do
		level = safevaluex(argvs, '__level__', 0)

		if func(node, **argvs) == False:
			return False

		# Recursive analysising children
		
		level += 1
		argvs['__level__'] = level

		children = safevalue(node, 'children')
		for child in children:
			if CCBParser.parseNode(child, func, **argvs) == False:
				return False

		return True


	@staticmethod
	def parseProps(props, func, **argvs):
		for p in props:
			if func(p) == False:
				return


	@staticmethod
	def parseKeyFrames(keyframes, func, **argvs):
		for kf in keyframes:
			if func(kf, **argvs) == False:
				return


	@staticmethod
	def defParseNodeFunc(node, **argvs):
		displayName             = safevalue(node, 'displayName')
		baseClass               = safevalue(node, 'baseClass')
		customClass             = safevalue(node, 'customClass')
		memberVarAssignmentType = safevalue(node, 'memberVarAssignmentType')
		memberVarAssignmentName = safevalue(node, 'memberVarAssignmentName')
		animatedProperties      = safevalue(node, 'animatedProperties')
		properties              = safevalue(node, 'properties')

		CCBParser.parseProps(properties, CCBParser.defParsePropFunc, **argvs)


	@staticmethod
	def defParsePropFunc(prop, **argvs):
		pname  = safevalue(p, 'name')
		ptype  = safevalue(p, 'type')
		pvalue = safevalue(p, 'value')


	@staticmethod
	def defParseSeqFunc(seq, **argvs):
		autoPlay        = safevalue(seq, 'autoPlay')
		callbackChannel = safevalue(seq, 'callbackChannel')

		keyframes       = safevalue(callbackChannel, 'keyframes')

		CCBParser.parseKeyFrames(keyframes, CCBParser.defParseKeyFrameFunc, **argvs)


	@staticmethod
	def defParseKeyFrameFunc(keyframe, **argvs):
		kfeasing = safevalue(keyframe, 'easing')
		kftype   = safevalue(keyframe, 'type')
		kftime   = safevalue(keyframe, 'time')
		kfvalue  = safevalue(keyframe, 'value')



def output(node, **argvs):
	displayName             = safevalue(node, 'displayName')
	baseClass               = safevalue(node, 'baseClass')
	customClass             = safevalue(node, 'customClass')
	memberVarAssignmentType = safevalue(node, 'memberVarAssignmentType')
	memberVarAssignmentName = safevalue(node, 'memberVarAssignmentName')
	animatedProperties      = safevalue(node, 'animatedProperties')
	properties              = safevalue(node, 'properties')


	space = '\t' * argvs['__level__']
	s = space + displayName
	if memberVarAssignmentType == 2:
		s += ': ' + memberVarAssignmentName

	if properties != None:
		for p in properties:
			pn = safevalue(p, 'name')
			pt = safevalue(p, 'type')
			if (pn == 'block' and pt == 'Block') or (pn == 'ccControl' and pt == 'BlockCCControl'):
				pv = safevalue(p, 'value')
				selector = pv[0]
				selectortype = pv[1]
				# TODO callback
				if selectortype == 2:
					s += ' | ' + selector
					break

	print s


def outputSeqCallback(seq, **argvs):
	autoPlay        = safevalue(seq, 'autoPlay')
	callbackChannel = safevalue(seq, 'callbackChannel')

	keyframes       = safevalue(callbackChannel, 'keyframes')

	for kf in keyframes:
		kftype      = safevalue(kf, 'type')

		if kftype == 10:
			kfvalue = safevalue(kf, 'value')
			v1      = kfvalue[0]
			v2      = kfvalue[1]
			if v2 == 2:
				print v1


def usage():
	me = sys.argv[0]
	print 'usage: ' + me + ' <CCB_FILE>'


def main():
	if len(sys.argv) < 2:
		usage()
		exit(0)

	ccb = sys.argv[1]
	parser = CCBParser(ccb)
	parser.parseCCNodes(output)
	parser.parseSeqs(outputSeqCallback)


if __name__ == '__main__':
	main()


del main, usage, sys, output, outputSeqCallback
