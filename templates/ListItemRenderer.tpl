-- Created by ${author} on ${date}

require "common/bvutil"


local MItemRendererExtend = import("common.miniui.MItemRendererExtend")
local ItemRendererFor${tpl['name']} = {}

function ItemRendererFor${tpl['name']}.extend(target)
	MItemRendererExtend.extend(target)
	
	function target:onActivate(target)
	end
	
	function target:onSelected(data)
	end
	
	function target:onUnselected(data)
	end

	function target:onEnter()
	end

	function target:onExit()
	end
	
	function target:onSetData(data)
		% if len(tpl['vars']) > 0:
		local view = self:getContentView()
		% endif

		## tpl = {'name': itemTplName, 'selectors': {selector, ...}, 'vars': {'varName': {'type': 'varType', 'tag': 'varTag', 'selector': 'varSelector'}, ...}}
		% for varName, varInfo in sorted(tpl['vars'].iteritems(), key = lambda d: d[1]['tag'] if 'tag' in d[1] else ''):
<%
		varType  = varInfo['type']
%>\
		% if 'tag' in varInfo:
<%
		varTag   = varInfo['tag']
%>\
		local ${varName} = tolua.cast(view:getChildByTag(${varTag}), "${varType}")
		% endif
		% endfor

		% for varName, varInfo in sorted(tpl['vars'].iteritems(), key = lambda d: d[0]):
		% if 'selector' in varInfo and varType in {'MControlButton', 'CCControlButton', 'CCControl'}:
<%
		varSelector = varInfo['selector']
%>\
		${varName}:removeHandleOfControlEvent(CCControlEventTouchUpInside)
		${varName}:addHandleOfControlEvent(function(node, event) self:${varSelector}(node, event) end, CCControlEventTouchUpInside)
		self.${varName} = ${varName}
		% endif
		% endfor

		% for varName, varInfo in sorted(tpl['vars'].iteritems(), key = lambda d: d[0]):
		% if varInfo['type'] in {'CCLabelTTF', 'MLabelTTF'}:
		${varName}:setString(loc_string("please_rename_this_key"))  -- REPLACE
		% endif
		% endfor
	end

	function target:destoryContentView()
		% for varName, varInfo in tpl['vars'].iteritems():
		% if 'selector' in varInfo:
		if self.${varInfo['selector']} then self.${varInfo['selector']}:removeHandleOfControlEvent(CCControlEventTouchUpInside) end
		% endif
		% endfor
	end

	% for varName, varInfo in tpl['vars'].iteritems():
	% if 'selector' in varInfo:
	function target:${varInfo['selector']}(node, event)
		self:getDispatcher():postNotification("${varInfo['selector']}")
	end

	% endif
	% endfor
end

return ItemRendererFor${tpl['name']}