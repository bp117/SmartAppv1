webpackJsonp([1,3],{

/***/ 185:
/***/ (function(module, exports) {

/*
	MIT License http://www.opensource.org/licenses/mit-license.php
	Author Tobias Koppers @sokra
*/
// css base code, injected by the css-loader
module.exports = function() {
	var list = [];

	// return the list of modules as css string
	list.toString = function toString() {
		var result = [];
		for(var i = 0; i < this.length; i++) {
			var item = this[i];
			if(item[2]) {
				result.push("@media " + item[2] + "{" + item[1] + "}");
			} else {
				result.push(item[1]);
			}
		}
		return result.join("");
	};

	// import a list of modules into the list
	list.i = function(modules, mediaQuery) {
		if(typeof modules === "string")
			modules = [[null, modules, ""]];
		var alreadyImportedModules = {};
		for(var i = 0; i < this.length; i++) {
			var id = this[i][0];
			if(typeof id === "number")
				alreadyImportedModules[id] = true;
		}
		for(i = 0; i < modules.length; i++) {
			var item = modules[i];
			// skip already imported module
			// this implementation is not 100% perfect for weird media query combinations
			//  when a module is imported multiple times with different media queries.
			//  I hope this will never occur (Hey this way we have smaller bundles)
			if(typeof item[0] !== "number" || !alreadyImportedModules[item[0]]) {
				if(mediaQuery && !item[2]) {
					item[2] = mediaQuery;
				} else if(mediaQuery) {
					item[2] = "(" + item[2] + ") and (" + mediaQuery + ")";
				}
				list.push(item);
			}
		}
	};
	return list;
};


/***/ }),

/***/ 194:
/***/ (function(module, exports) {

/*
	MIT License http://www.opensource.org/licenses/mit-license.php
	Author Tobias Koppers @sokra
*/
var stylesInDom = {},
	memoize = function(fn) {
		var memo;
		return function () {
			if (typeof memo === "undefined") memo = fn.apply(this, arguments);
			return memo;
		};
	},
	isOldIE = memoize(function() {
		return /msie [6-9]\b/.test(self.navigator.userAgent.toLowerCase());
	}),
	getHeadElement = memoize(function () {
		return document.head || document.getElementsByTagName("head")[0];
	}),
	singletonElement = null,
	singletonCounter = 0,
	styleElementsInsertedAtTop = [];

module.exports = function(list, options) {
	if(typeof DEBUG !== "undefined" && DEBUG) {
		if(typeof document !== "object") throw new Error("The style-loader cannot be used in a non-browser environment");
	}

	options = options || {};
	// Force single-tag solution on IE6-9, which has a hard limit on the # of <style>
	// tags it will allow on a page
	if (typeof options.singleton === "undefined") options.singleton = isOldIE();

	// By default, add <style> tags to the bottom of <head>.
	if (typeof options.insertAt === "undefined") options.insertAt = "bottom";

	var styles = listToStyles(list);
	addStylesToDom(styles, options);

	return function update(newList) {
		var mayRemove = [];
		for(var i = 0; i < styles.length; i++) {
			var item = styles[i];
			var domStyle = stylesInDom[item.id];
			domStyle.refs--;
			mayRemove.push(domStyle);
		}
		if(newList) {
			var newStyles = listToStyles(newList);
			addStylesToDom(newStyles, options);
		}
		for(var i = 0; i < mayRemove.length; i++) {
			var domStyle = mayRemove[i];
			if(domStyle.refs === 0) {
				for(var j = 0; j < domStyle.parts.length; j++)
					domStyle.parts[j]();
				delete stylesInDom[domStyle.id];
			}
		}
	};
}

function addStylesToDom(styles, options) {
	for(var i = 0; i < styles.length; i++) {
		var item = styles[i];
		var domStyle = stylesInDom[item.id];
		if(domStyle) {
			domStyle.refs++;
			for(var j = 0; j < domStyle.parts.length; j++) {
				domStyle.parts[j](item.parts[j]);
			}
			for(; j < item.parts.length; j++) {
				domStyle.parts.push(addStyle(item.parts[j], options));
			}
		} else {
			var parts = [];
			for(var j = 0; j < item.parts.length; j++) {
				parts.push(addStyle(item.parts[j], options));
			}
			stylesInDom[item.id] = {id: item.id, refs: 1, parts: parts};
		}
	}
}

function listToStyles(list) {
	var styles = [];
	var newStyles = {};
	for(var i = 0; i < list.length; i++) {
		var item = list[i];
		var id = item[0];
		var css = item[1];
		var media = item[2];
		var sourceMap = item[3];
		var part = {css: css, media: media, sourceMap: sourceMap};
		if(!newStyles[id])
			styles.push(newStyles[id] = {id: id, parts: [part]});
		else
			newStyles[id].parts.push(part);
	}
	return styles;
}

function insertStyleElement(options, styleElement) {
	var head = getHeadElement();
	var lastStyleElementInsertedAtTop = styleElementsInsertedAtTop[styleElementsInsertedAtTop.length - 1];
	if (options.insertAt === "top") {
		if(!lastStyleElementInsertedAtTop) {
			head.insertBefore(styleElement, head.firstChild);
		} else if(lastStyleElementInsertedAtTop.nextSibling) {
			head.insertBefore(styleElement, lastStyleElementInsertedAtTop.nextSibling);
		} else {
			head.appendChild(styleElement);
		}
		styleElementsInsertedAtTop.push(styleElement);
	} else if (options.insertAt === "bottom") {
		head.appendChild(styleElement);
	} else {
		throw new Error("Invalid value for parameter 'insertAt'. Must be 'top' or 'bottom'.");
	}
}

function removeStyleElement(styleElement) {
	styleElement.parentNode.removeChild(styleElement);
	var idx = styleElementsInsertedAtTop.indexOf(styleElement);
	if(idx >= 0) {
		styleElementsInsertedAtTop.splice(idx, 1);
	}
}

function createStyleElement(options) {
	var styleElement = document.createElement("style");
	styleElement.type = "text/css";
	insertStyleElement(options, styleElement);
	return styleElement;
}

function createLinkElement(options) {
	var linkElement = document.createElement("link");
	linkElement.rel = "stylesheet";
	insertStyleElement(options, linkElement);
	return linkElement;
}

function addStyle(obj, options) {
	var styleElement, update, remove;

	if (options.singleton) {
		var styleIndex = singletonCounter++;
		styleElement = singletonElement || (singletonElement = createStyleElement(options));
		update = applyToSingletonTag.bind(null, styleElement, styleIndex, false);
		remove = applyToSingletonTag.bind(null, styleElement, styleIndex, true);
	} else if(obj.sourceMap &&
		typeof URL === "function" &&
		typeof URL.createObjectURL === "function" &&
		typeof URL.revokeObjectURL === "function" &&
		typeof Blob === "function" &&
		typeof btoa === "function") {
		styleElement = createLinkElement(options);
		update = updateLink.bind(null, styleElement);
		remove = function() {
			removeStyleElement(styleElement);
			if(styleElement.href)
				URL.revokeObjectURL(styleElement.href);
		};
	} else {
		styleElement = createStyleElement(options);
		update = applyToTag.bind(null, styleElement);
		remove = function() {
			removeStyleElement(styleElement);
		};
	}

	update(obj);

	return function updateStyle(newObj) {
		if(newObj) {
			if(newObj.css === obj.css && newObj.media === obj.media && newObj.sourceMap === obj.sourceMap)
				return;
			update(obj = newObj);
		} else {
			remove();
		}
	};
}

var replaceText = (function () {
	var textStore = [];

	return function (index, replacement) {
		textStore[index] = replacement;
		return textStore.filter(Boolean).join('\n');
	};
})();

function applyToSingletonTag(styleElement, index, remove, obj) {
	var css = remove ? "" : obj.css;

	if (styleElement.styleSheet) {
		styleElement.styleSheet.cssText = replaceText(index, css);
	} else {
		var cssNode = document.createTextNode(css);
		var childNodes = styleElement.childNodes;
		if (childNodes[index]) styleElement.removeChild(childNodes[index]);
		if (childNodes.length) {
			styleElement.insertBefore(cssNode, childNodes[index]);
		} else {
			styleElement.appendChild(cssNode);
		}
	}
}

function applyToTag(styleElement, obj) {
	var css = obj.css;
	var media = obj.media;

	if(media) {
		styleElement.setAttribute("media", media)
	}

	if(styleElement.styleSheet) {
		styleElement.styleSheet.cssText = css;
	} else {
		while(styleElement.firstChild) {
			styleElement.removeChild(styleElement.firstChild);
		}
		styleElement.appendChild(document.createTextNode(css));
	}
}

function updateLink(linkElement, obj) {
	var css = obj.css;
	var sourceMap = obj.sourceMap;

	if(sourceMap) {
		// http://stackoverflow.com/a/26603875
		css += "\n/*# sourceMappingURL=data:application/json;base64," + btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap)))) + " */";
	}

	var blob = new Blob([css], { type: "text/css" });

	var oldSrc = linkElement.href;

	linkElement.href = URL.createObjectURL(blob);

	if(oldSrc)
		URL.revokeObjectURL(oldSrc);
}


/***/ }),

/***/ 333:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(450);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(194)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../node_modules/css-loader/index.js?{\"sourceMap\":false,\"importLoaders\":1}!../../../node_modules/postcss-loader/index.js!./loading-bars.css", function() {
			var newContent = require("!!../../../node_modules/css-loader/index.js?{\"sourceMap\":false,\"importLoaders\":1}!../../../node_modules/postcss-loader/index.js!./loading-bars.css");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 334:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(451);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(194)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../node_modules/css-loader/index.js?{\"sourceMap\":false,\"importLoaders\":1}!../../../node_modules/postcss-loader/index.js!./riliwan-rabo.css", function() {
			var newContent = require("!!../../../node_modules/css-loader/index.js?{\"sourceMap\":false,\"importLoaders\":1}!../../../node_modules/postcss-loader/index.js!./riliwan-rabo.css");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 335:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(452);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(194)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../node_modules/css-loader/index.js?{\"sourceMap\":false,\"importLoaders\":1}!../../../node_modules/postcss-loader/index.js!./style.css", function() {
			var newContent = require("!!../../../node_modules/css-loader/index.js?{\"sourceMap\":false,\"importLoaders\":1}!../../../node_modules/postcss-loader/index.js!./style.css");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 450:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(185)();
// imports


// module
exports.push([module.i, ".splash {\n    position: absolute;\n    z-index: 2000;\n    background: white;\n    color: gray;\n    top: 0;\n    bottom: 0;\n    left: 0;\n    right: 0\n}\n\n.splash-title {\n    text-align: center;\n    max-width: 500px;\n    margin: 15% auto;\n    padding: 20px\n}\n\n.splash-title h1{\n    font-size: 26px\n}\n\n.color-line {\n    border-radius:4px 4px 0 0\n}", ""]);

// exports


/***/ }),

/***/ 451:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(185)();
// imports
exports.push([module.i, "@import url(http://fonts.googleapis.com/css?family=Roboto+Condensed:400,700);", ""]);

// module
exports.push([module.i, "/* written by riliwan balogun http://www.facebook.com/riliwan.rabo*/\n.board{\n    width: 75%;\n    margin: 60px auto;\n    height: 500px;\n    background: #fff;\n    /*box-shadow: 10px 10px #ccc,-10px 20px #ddd;*/\n}\n.board .nav-tabs {\n    position: relative;\n    /* border-bottom: 0; */\n    /* width: 80%; */\n    margin: 40px auto;\n    margin-bottom: 0;\n    box-sizing: border-box;\n\n}\n\n.board > div.board-inner{\n    background: #fafafa url(http://subtlepatterns.com/patterns/geometry2.png);\n    background-size: 30%;\n}\n\np.narrow{\n    width: 60%;\n    margin: 10px auto;\n}\n\n.liner{\n    height: 2px;\n    background: #ddd;\n    position: absolute;\n    width: 80%;\n    margin: 0 auto;\n    left: 0;\n    right: 0;\n    top: 50%;\n    z-index: 1;\n}\n\n.nav-tabs > li.active > a, .nav-tabs > li.active > a:hover, .nav-tabs > li.active > a:focus {\n    color: #555555;\n    cursor: default;\n    /* background-color: #ffffff; */\n    border: 0;\n    border-bottom-color: transparent;\n}\n\nspan.round-tabs{\n    width: 70px;\n    height: 70px;\n    line-height: 70px;\n    display: inline-block;\n    border-radius: 100px;\n    background: white;\n    z-index: 2;\n    position: absolute;\n    left: 0;\n    text-align: center;\n    font-size: 25px;\n}\n\nspan.round-tabs.one{\n    color: rgb(34, 194, 34);border: 2px solid rgb(34, 194, 34);\n}\n\nli.active span.round-tabs.one{\n    background: #fff !important;\n    border: 2px solid #ddd;\n    color: rgb(34, 194, 34);\n}\n\nspan.round-tabs.two{\n    color: #febe29;border: 2px solid #febe29;\n}\n\nli.active span.round-tabs.two{\n    background: #fff !important;\n    border: 2px solid #ddd;\n    color: #febe29;\n}\n\nspan.round-tabs.three{\n    color: #3e5e9a;border: 2px solid #3e5e9a;\n}\n\nli.active span.round-tabs.three{\n    background: #fff !important;\n    border: 2px solid #ddd;\n    color: #3e5e9a;\n}\n\nspan.round-tabs.four{\n    color: #f1685e;border: 2px solid #f1685e;\n}\n\nli.active span.round-tabs.four{\n    background: #fff !important;\n    border: 2px solid #ddd;\n    color: #f1685e;\n}\n\nspan.round-tabs.five{\n    color: #999;border: 2px solid #999;\n}\n\nli.active span.round-tabs.five{\n    background: #fff !important;\n    border: 2px solid #ddd;\n    color: #999;\n}\n\n.nav-tabs > li.active > a span.round-tabs{\n    background: #fafafa;\n}\n.nav-tabs > li {\n    /*width: 20%;*/\n    width: 25%;\n}\n/*li.active:before {\n    content: \" \";\n    position: absolute;\n    left: 45%;\n    opacity:0;\n    margin: 0 auto;\n    bottom: -2px;\n    border: 10px solid transparent;\n    border-bottom-color: #fff;\n    z-index: 1;\n    transition:0.2s ease-in-out;\n}*/\n.nav-tabs > li:after {\n    content: \" \";\n    position: absolute;\n    left: 45%;\n   opacity:0;\n    margin: 0 auto;\n    bottom: 0px;\n    border: 5px solid transparent;\n    border-bottom-color: #ddd;\n    -webkit-transition: 0.1s ease-in-out;\n    transition:0.1s ease-in-out;\n    \n}\n.nav-tabs > li.active:after {\n    content: \" \";\n    position: absolute;\n    left: 45%;\n   opacity:1;\n    margin: 0 auto;\n    bottom: 0px;\n    border: 10px solid transparent;\n    border-bottom-color: #ddd;\n    \n}\n.nav-tabs > li a{\n   width: 70px;\n   height: 70px;\n   margin: 20px auto;\n   border-radius: 100%;\n   padding: 0;\n}\n\n.nav-tabs > li a:hover{\n    background: transparent;\n}\n\n.tab-content .tab-pane{\n   position: relative;\n/*padding-top: 50px;*/\n}\n.tab-content .head{\n    font-family: 'Roboto Condensed', sans-serif;\n    font-size: 25px;\n    text-transform: uppercase;\n    padding-bottom: 10px;\n}\n.btn-outline-rounded{\n    padding: 10px 40px;\n    margin: 20px 0;\n    border: 2px solid transparent;\n    border-radius: 25px;\n}\n\n.btn.green{\n    background-color:#5cb85c;\n    /*border: 2px solid #5cb85c;*/\n    color: #ffffff;\n}\n\n\n\n@media( max-width : 585px ){\n    \n    .board {\nwidth: 90%;\nheight:auto !important;\n}\n    span.round-tabs {\n        font-size:16px;\nwidth: 50px;\nheight: 50px;\nline-height: 50px;\n    }\n    .tab-content .head{\n        font-size:20px;\n        }\n    .nav-tabs > li a {\nwidth: 50px;\nheight: 50px;\nline-height:50px;\n}\n\n.nav-tabs > li.active:after {\ncontent: \" \";\nposition: absolute;\nleft: 35%;\n}\n\n.btn-outline-rounded {\n    padding:12px 20px;\n    }\n}\n", ""]);

// exports


/***/ }),

/***/ 452:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(185)();
// imports


// module
exports.push([module.i, ".btn-default {\n    border-color: #ccc;\n}\n\n.tab-content .choice {\n  text-align: center;\n  cursor: pointer;\n  margin-top: 38px;\n}\n\n.tab-content .choice i {\n    font-size: 32px;\n    line-height: 55px;\n}\n\n.btn-radio {\n\twidth: 100%;\n}\n.img-radio {\n\topacity: 0.8;\n\tmargin-bottom: 5px;\n}\n\n.space-20 {\n    margin-top: 20px;\n}\n\n/* active buttons */\n#status-buttons a.active span.round-tabs.one { \n    background: rgb(34, 194, 34); \n    color: #fff\n}\n\n#status-buttons a.active span.round-tabs.two { \n    background: #febe29; \n    color: #fff\n}\n\n#status-buttons a.active span.round-tabs.three { \n    background: #3e5e9a; \n    color: #fff\n}\n\n#status-buttons a.active span.round-tabs.four { \n    background: #f1685e; \n    color: #fff\n}\n\n\n.iradio_buttons {\n    display: inline-block;\n    vertical-align: middle;\n    margin: 0;\n    padding: 0;\n    width: 22px;\n    height: 22px;\n    background: #febe29 no-repeat;\n    border: none;\n    cursor: pointer;\n}\n.iradio_buttons {\n    background-position: -120px 0;\n}\n.iradio_buttons.hover {\n    background-position: -144px 0;\n}\n.iradio_buttons.checked {\n    background-position: -168px 0;\n}\n.form-group{\n    margin-bottom: 3px;\n}", ""]);

// exports


/***/ }),

/***/ 519:
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(335);
__webpack_require__(334);
module.exports = __webpack_require__(333);


/***/ })

},[519]);
//# sourceMappingURL=styles.bundle.js.map