<%!
def getListBaseName(name):
	if name.find('m_list') == 0:
		return name[len('m_list'):]
	else:
		return name[len('list'):]


def safevalue(d, k, df = None):
		if k in d:
			return d[k]
		else:
			return df

%>\
-- Created by ${author} on ${date}

require "common/functions"
require "common/bvutil"
require "common/ui"
require "common/cocos2dx/CCNodeExtend"


local ${className} = class("${className}", function()
	local base = CCNodeExtend.extend(CBaseLayer:create("${className}"))
	return base
end)

function ${className}:ctor()
	-- TODO: init member vars here
	self.m_bClosing = false

	self:addChild(MaskLayer:node())

	% for selector in selectors:
	self.${selector} = function() return self:${selector}_h() end
	% endfor
	% for callback in callbacks:
	self.${callback} = function() return self:${callback}_h() end
	% endfor

	local path = getScriptUIResourcePath("${luaPkgName}", "${resDescName}")
	local node = CCBuilderReaderLoad(path, CCBProxy:create(), self)
	self:setPanel(node)
	self:addChild(node)

	self:setNodeEventEnabled(true)
	self:registerScriptWillShowHandler(function() return self:willShow() end)
	self:registerScriptWillCloseHandler(function() return self:willClose() end)

	## {'varName': 'varType', ...}
	% for varName, varType in sorted(vars.iteritems(), key = lambda d: d[0]):
	self.${varName} = tolua.cast(self.${varName}, "${varType}")
	% endfor

	% for varName, varType in vars.iteritems():
	% if varType in {'CCLabelTTF', 'MLabelTTF'}:
	self.${varName}:setString(loc_string("please_rename_this_key"))  -- REPLACE
	% endif
	% endfor

	## lists = {'listName': [{'name': itemTplName, 'selectors': {selector, ...}, 'vars': {'varName': {'type': 'varType', 'tag': 'varTag', 'selector': 'varSelector'}, ...}}, ...], ...}
	% for listName, itemTpls in lists.iteritems():
<%
	itemTplName = itemTpls[0]['name']
%>\
	-- init ${itemTplName} list
	local irFor${itemTplName} = import("${luaPkgName}.ItemRendererFor${itemTplName}")
	function irFuncFor${itemTplName}(itemRenderer)
		irFor${itemTplName}.extend(itemRenderer)
		itemRenderer:setNodeEventEnabled(true)
	end

	local irFactoryFor${itemTplName} = MComplexItemRendererFactory:create()
	irFactoryFor${itemTplName}:registerScriptCreateObjectHandler(irFuncFor${itemTplName})

	self.${listName}:setVisible(true)

	self.${listName}_l = MComplexList:createList(self.${listName}, 1, irFactoryFor${itemTplName})  -- REPLACE #2 argv
	self.${listName}_l:retain()

	% endfor
end

function ${className}:willShow()
	audio_effect(AUDIO_POPUP_PANEL)
	self:setCanBeClosed(false)
	self.m_bClosing = false
	self.mAnimationManager:runAnimationsForSequenceNamed("appear") -- REPLACE
	self:alignToCenter()
end

function ${className}:willClose()
	if self.m_bClosing == true then
		return
	end
	self.m_bClosing = true

	audio_effect(AUDIO_CLOSE_PANEL)
	self.mAnimationManager:runAnimationsForSequenceNamed("exit") -- REPLACE
	
end

function ${className}:onEnter()
	self:willShow()
	tolua.cast(GameScene:sharedInstance():getHUDLayer(),"HUDLayer"):MoveOut()

	% for listName, itemTpls in lists.iteritems():
<%
	itemTpl = itemTpls[0]
	itemTplName = itemTpl['name']
	itemTplVars = safevalue(itemTpl, 'vars', dict())
	itemTplSelectors = safevalue(itemTpl, 'selectors', set())
	listBaseName = getListBaseName(listName)
%>\
	% if len(itemTplSelectors) > 0:
	local dispFor${listBaseName} = tolua.cast(self.${listName}_l:getDispatcher(), "CCNotificationCenter")
	% for varName, varInfo in itemTplVars.iteritems():
	% if 'selector' in varInfo:
	dispFor${listBaseName}:registerScriptObserver(self, function(node, event) return self:${varInfo['selector']}(node, event) end, "${varInfo['selector']}")
	% endif
	% endfor

	% endif
	% endfor
end

function ${className}:onExit()
	tolua.cast(GameScene:sharedInstance():getHUDLayer(),"HUDLayer"):MoveIn()

	% for listName, itemTpls in lists.iteritems():
<%
	itemTpl = itemTpls[0]
	itemTplName = itemTpl['name']
	itemTplVars = safevalue(itemTpl, 'vars', dict())
	itemTplSelectors = safevalue(itemTpl, 'selectors', set())
	listBaseName = getListBaseName(listName)
%>\

	% if len(itemTplSelectors) > 0:
	local dispFor${listBaseName} = tolua.cast(self.${listName}_l:getDispatcher(), "CCNotificationCenter")
	% for varName, varInfo in itemTplVars.iteritems():
	% if 'selector' in varInfo:
	dispFor${listBaseName}:unregisterScriptObserver(self, "${varInfo['selector']}")
	% endif
	% endfor
	% endif
	if self.${listName}_l then self.${listName}_l:release() end

	% endfor
end
% for listName, itemTpls in lists.iteritems():
<%
itemTpl = itemTpls[0]
itemTplName = itemTpl['name']
itemTplVars = safevalue(itemTpl, 'vars', dict())
itemTplSelectors = safevalue(itemTpl, 'selectors', set())
%>\
% if len(itemTplSelectors) > 0:

-- ${listName} selectors
% for varName, varInfo in itemTplVars.iteritems():
% if 'selector' in varInfo:
function ${className}:${varInfo['selector']}(node, event)
end

% endif
% endfor
% endif
% endfor
## {'selector', ...}
% if len(selectors) > 0:

-- selectors
% for selector in selectors:
function ${className}:${selector}_h()
end

% endfor
% endif
% if len(callbacks) > 0:
-- callbacks
## {'callback', ...}
% for callback in callbacks:
function ${className}:${callback}_h()
end

% endfor
% endif
return ${className}