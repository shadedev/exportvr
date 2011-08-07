#
# -*- coding: utf-8 -*-
# @title \en Export Panorama VR HTML \enden
# @title \ja Panorama VR HTML エクスポート \endja
# @description \en \enden
# @description \ja \endja
# @version 0.4.0
#

import os
import math
import time

try:
	import numpy
except ImportError, e:
	print _('error_import_numpy_failed')
	raise

SCRIPT_UUID = "c50b3d49-6573-447c-96d2-edcf903f6bf8"

class Settings:
	pan_default = 0.0
	pan_max = 360.0
	pan_min = 0.0
	tilt_default = 0.0
	tilt_max = 45.0
	tilt_min = -45.0
	fov_default = 40.0
	fov_max = 90.0
	fov_min = 40.0
	render_hemisphere = False
	makefolder = False
	output_path = None
	extension = 0
settings = Settings
defaults = Settings

def check_settings (s):
	if s.pan_min < 0 or s.pan_max < s.pan_min or s.pan_default < s.pan_min: return False
	if s.tilt_min < -90 or s.tilt_max < s.tilt_min or s.tilt_default < s.tilt_min: return False
	if s.fov_min < 0 or s.fov_max < s.fov_min or s.fov_default < s.fov_min: return False
	return True

def output_extension ():
	extensions = {0:'.jpg', 1:'.png'}
	return extensions[settings.extension]
def stepX (speed):
	return speed/settings.number_of_col
def stepY (speed):
	return speed/settings.number_of_row

class RenderingInfo:
	start_time = 0
	total_time = 0
	total_frames = 0
	average_time = 0
	image_size = (320, 240)
	view_size = (640, 640)
renderinfo = RenderingInfo

def get_lang ():
	import platform
	if platform.system() == 'Windows':
		from locale import windows_locale
		return windows_locale[xshade.preference().langid][0:2]
	elif platform.system() == 'Darwin':
		try:
			return xshade.preference().locale # 12.0.3 or later.
		except AttributeError:
			if os.environ['__CF_USER_TEXT_ENCODING'].split(':')[2] == '14':
				return 'ja'
			return 'en'
	return 'ja'

def get_text (text):
	texts = {
		'output_folder':{'ja':'出力先フォルダ', 'en':'Output Folder'},
		'pan':{'ja':'水平方向', 'en':'Pan'},
		'tilt':{'ja':'垂直方向', 'en':'Tilt'},
		'fov':{'ja':'画角', 'en':'Field of view'},
		'default':{'ja':'初期値', 'en':'Default'},
		'max':{'ja':'最大', 'en':'Max'},
		'min':{'ja':'最小', 'en':'Min'},
		'make_scenename_subfolder':{'ja':'出力先フォルダにシーン名のサブフォルダを作成', 'en':'Make scene file name subfolder in the output folder.'},
		'error_output_folder_not_found':{'ja':'エラー: 出力先フォルダを指定してください.', 'en':'Error: Output folder not found.'},
		'error_invalid_settings':{'ja':'エラー: 不正な値が指定されています.', 'en':'Error: Invalid paramter.'},
		'error_import_numpy_failed':{'ja':'エラー: numpyがインストールされていません。Shadeのアップデートを行ってください.', 'en':'Error: import numpy failed.'},
		'done':{'ja':'完了', 'en':'Done'},
		'canceled':{'ja':'キャンセル', 'en':'Canceled'},
		'panoramavr_option':{'ja':'Panorama VR オプション', 'en':'Panorama VR'},
		'output_option':{'ja':'出力オプション', 'en':'Output'},
		'untitled':{'ja':'名称未設定', 'en':'Untitled'},
		'extensions':{'ja':'出力フォーマット/JPEG(.jpg)/PNG(.png)', 'en':'Output Format/JPEG(.jpg)/PNG(.png)'}
	}
	lang = get_lang()
	try:
		return texts[text][lang]
	except KeyError:
		print 'Warning: Missing localized string: %(text)s (lang: %(lang)s) ' % vars()
		return text
_ = get_text

def get_default_path ():
	import platform
	if platform.system() == 'Windows':
		if platform.version()[0] < 6:
			return os.path.join(os.expanduser('~'), 'My Documents') # Windows XP
	return os.path.join(os.path.expanduser('~'), 'Documents')

def open_option_dialog ():
	global settings
	dialog = xshade.create_dialog_with_uuid(SCRIPT_UUID)
	# Panoramavr option
	#dialog.begin_group(_('pan'))
	#pan_default_id = dialog.append_float(_('default'), '')
	#pan_max_id = dialog.append_float(_('max'), '')
	#pan_min_id = dialog.append_float(_('min'))
	#dialog.end_group()
	#dialog.begin_group(_('tilt'))
	#tilt_default_id = dialog.append_float(_('default'), '')
	#tilt_max_id = dialog.append_float(_('max'), '')
	#tilt_min_id = dialog.append_float(_('min'))
	#dialog.end_group()
	#dialog.begin_group(_('fov'))
	#fov_default_id = dialog.append_float(_('default'), '')
	#fov_max_id = dialog.append_float(_('max'), '')
	#fov_min_id = dialog.append_float(_('min'))
	#dialog.end_group()
	# Output option
	dialog.begin_group(_('output_option'))
	path_id = dialog.append_path(_('output_folder'))
	makefolder_id = dialog.append_bool(_('make_scenename_subfolder'))
	extension_id = dialog.append_selection(_('extensions'))
	dialog.end_group()
	# set_value
	#dialog.set_value(pan_default_id, settings.pan_default)
	#dialog.set_value(pan_max_id, settings.pan_max)
	#dialog.set_value(pan_min_id, settings.pan_min)
	#dialog.set_value(tilt_default_id, settings.tilt_default)
	#dialog.set_value(tilt_max_id, settings.tilt_max)
	#dialog.set_value(tilt_min_id, settings.tilt_min)
	#dialog.set_value(fov_default_id, settings.fov_default)
	#dialog.set_value(fov_max_id, settings.fov_max)
	#dialog.set_value(fov_min_id, settings.fov_min)
	if settings.output_path == None: dialog.set_value(path_id, get_default_path())
	dialog.set_value(makefolder_id, settings.makefolder)
	# set_default_value
	#dialog.set_default_value(pan_default_id, defaults.pan_default)
	#dialog.set_default_value(pan_max_id, defaults.pan_max)
	#dialog.set_default_value(pan_min_id, defaults.pan_min)
	#dialog.set_default_value(tilt_default_id, defaults.tilt_default)
	#dialog.set_default_value(tilt_max_id, defaults.tilt_max)
	#dialog.set_default_value(tilt_min_id, defaults.tilt_min)
	#dialog.set_default_value(fov_default_id, defaults.fov_default)
	#dialog.set_default_value(fov_max_id, defaults.fov_max)
	#dialog.set_default_value(fov_min_id, defaults.fov_min)
	dialog.set_default_value(path_id, get_default_path())
	dialog.set_default_value(makefolder_id, defaults.makefolder)
	dialog.set_default_value(extension_id, defaults.extension)
	# dialog option
	dialog.append_default_button()
	if not dialog.ask('Panorama VR'):
		return False
	#settings.pan_default = dialog.get_value(pan_default_id)
	#settings.pan_max = dialog.get_value(pan_max_id)
	#settings.pan_min = dialog.get_value(pan_min_id)
	#settings.tilt_default = dialog.get_value(tilt_default_id)
	#settings.tilt_max = dialog.get_value(tilt_max_id)
	#settings.tilt_min = dialog.get_value(tilt_min_id)
	#settings.fov_default = dialog.get_value(fov_default_id)
	#settings.fov_max = dialog.get_value(fov_max_id)
	#settings.fov_min = dialog.get_value(fov_min_id)
	settings.output_path = decode(dialog.get_value(path_id))
	settings.makefolder = dialog.get_value(makefolder_id)
	settings.extension = dialog.get_value(extension_id)
	if not os.path.exists(settings.output_path):
		parent = os.path.dirname(settings.output_path)
		if not os.path.exists(parent):
			print _('error_output_folder_not_found')
			return False
		os.mkdir(settings.output_path)
	if not check_settings(settings):
		print _('error_invalid_settings')
		return False
	return True

def translate (v):
	t = numpy.matrix(numpy.identity(4))
	t[3, 0] = v[0]
	t[3, 1] = v[1]
	t[3, 2] = v[2]
	return t

def distance (v):
	return numpy.linalg.norm(v)

def normalize (v):
	return v / distance(v)

def rotate_ (d, c, s):
	t = numpy.zeros((4,4))
	dd = normalize(d)
	l = dd[0]
	m = dd[1]
	n = dd[2]
	l2 = l * l
	m2 = m * m
	n2 = n * n
	t[0, 1] = l * m * (1.0 - c) + n * s
	t[0, 2] = l * n * (1.0 - c) - m * s
	t[1, 0] = l * m * (1.0 - c) - n * s
	t[1, 1] = m2 + (1.0 - m2) * c;
	t[1, 2] = m * n * (1.0 - c) + l * s
	t[2, 0] = l * n * (1.0 - c) + m * s
	t[2, 1] = m * n * (1.0 - c) - l * s
	t[2, 2] = n2 + (1.0 - n2) * c
	t[3, 3] = 1.0
	return t

def rotate (target, axis, r):
	return translate(-target) * rotate_(axis, numpy.cos(r), numpy.sin(r)) * translate(target)

def vec4 (v3):
	return numpy.array(list(v3) + [0.0])

def rotate_eye (eye, target, frame, rotations, row):
	delta = 0.0002
	rotated_eye = eye
	n = frame
	maxN = rotations
	if 1 < row:
		maxN = (maxN + 1) / row - 1
		r = math.pi/2.0 - ((math.pi / (row - 1)) * (n / (maxN + 1)))
		r = max(r, -math.pi/2.0 + delta)
		r = min(r,  math.pi/2.0 - delta)
		axis = normalize(numpy.cross((rotated_eye - target)[:3], numpy.array((0, 1, 0))))
		rotated_eye = numpy.array(rotated_eye * rotate(target, axis, r))
	n = n % (maxN + 1)
	r = (2.0 * math.pi) / (maxN + 1) * n
	rotated_eye = numpy.array(rotated_eye * rotate(target, numpy.array((0, 1, 0)), r))
	return tuple(rotated_eye[0, :3])

# Windows版で日本語ファイルパスを扱う場合、Pythonには unicode 文字列で　Shadeには　utf-8　文字列で渡す.
# ファイルパスはdecodeでunicode化し、Shadeに渡すときにencodeでutf-8にする.

def decode (s):
	import platform
	if platform.system() == 'Windows':
		return unicode(s, 'utf-8')
	return s

def encode (s):
	import platform
	if platform.system() == 'Windows':
		return s.encode('utf-8')
	return s

def angle_of_view (rendering, camera):
	film_35mm_h = 36.0
	film_35mm_v = 24.0
	zoom = camera.zoom
	image_w = float(rendering.image_size[0])
	image_h = float(rendering.image_size[1])
	fsize_w = 0.0
	fsize_h = 0.0
	if image_w > image_h:
		fsize_w = film_35mm_h
		fsize_h = (film_35mm_h / image_w) * image_h
	else:
		fsize_w = (film_35mm_h / image_h) * image_w
		fsize_h = film_35mm_h
	d = math.sqrt(math.pow(fsize_w, 2) + math.pow(fsize_h, 2))
	return (2*math.atan(fsize_w/(2*zoom))*(180/math.pi), math.atan(fsize_h/(2*zoom))*(180/math.pi))

def is_pow2 (x):
    if x == 0: return False
    return (x & (x - 1)) == 0

def closest_pow2 (x):
    if is_pow2(x): return x
    n = 1
    while True:
        pow2 = 2**n
        if x < pow2: return pow2
        n += 1
    return None

def start_rendering (scene, file_path):
	global renderinfo
	animation_settings = scene.animation_settings
	# レンダリング前の設定を保存.
	saved_eye = scene.camera.eye
	saved_active_shapes = scene.active_shapes
	saved_panorama = scene.rendering.panorama_projection
	scene.select_all()
	try:
		fov = angle_of_view(scene.rendering, scene.camera)
		image_size = scene.rendering.image_size
		renderinfo.view_size = image_size
		width = min(closest_pow2(int(image_size[0]*360/fov[0])), 1024)
		height = min(closest_pow2(int(image_size[1]*90/fov[1])), 1024)
		scene.rendering.image_size = (width, height)
		renderinfo.image_size = scene.rendering.image_size
		scene.rendering.panorama_projection = 1
		scene.rendering.transparency_affects_alpha = False
		renderinfo.start_time = time.time()
		scene.rendering.render()
		renderinfo.total_time = time.time() - renderinfo.start_time
		renderinfo.total_frames = 1
		renderinfo.average_time = renderinfo.total_time
		scene.save_image(encode(file_path))
	finally:
		# レンダリング前の設定を復帰.
		scene.camera.eye = saved_eye
		scene.active_shapes = saved_active_shapes
		scene.rendering.image_size = image_size
		scene.rendering.panorama_projection = saved_panorama

def version_info ():
	try:
		return xshade.shade().version_info
	except AttributeError:
		return 'Shade 10 (%d)' % xshade.shade().version

def write_index_html (index_path):
	f = open(index_path, "w")
	f.write("""<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<meta name="viewport" content="width=1024; maximum-scale=1.2;" />
	<meta name="generator" content=\"""" + version_info() + """\">
	<title>HTML5 Panorama VR</title>
	<style>
	</style>
	<script type="text/javascript" src="glMatrix-0.9.5.min.js"></script>
	<script type="text/javascript" src="webgl-utils.js"></script>
<script id="per-fragment-lighting-fs" type="x-shader/x-fragment">
#ifdef GL_ES
    precision highp float;
#endif
varying vec2 vTextureCoord;
varying vec3 vTransformedNormal;
varying vec4 vPosition;
uniform sampler2D uSampler;
void main(void) {
	vec4 fragmentColor = texture2D(uSampler, vec2(vTextureCoord.s, vTextureCoord.t));
	gl_FragColor = vec4(fragmentColor.rgb, fragmentColor.a);
}
</script>
<script id="per-fragment-lighting-vs" type="x-shader/x-vertex">
attribute vec3 aVertexPosition;
attribute vec3 aVertexNormal;
attribute vec2 aTextureCoord;
uniform mat4 uMVMatrix;
uniform mat4 uPMatrix;
uniform mat3 uNMatrix;
varying vec2 vTextureCoord;
varying vec3 vTransformedNormal;
varying vec4 vPosition;
void main(void) {
	vPosition = uMVMatrix * vec4(aVertexPosition, 1.0);
	gl_Position = uPMatrix * vPosition;
	vTextureCoord = aTextureCoord;
	vTransformedNormal = uNMatrix * aVertexNormal;
}
</script>
	<script>
		function addEventListener_ (obj, type, listener, useCapture) {
			if (obj.addEventListener) { obj.addEventListener(type, listener, useCapture); } // all browsers, except IE.
			else if (obj.attachEvent) { obj.attachEvent('on' + type, listener); } // IE.
		}
		function removeEventListener_ (obj, type, listener, useCapture) {
			if (obj.removeEventListener) { obj.removeEventListener(type, listener, useCapture); } // all browsers, except IE.
			else if (obj.detachEvent) { obj.detachEvent('on' + type, listener); } // IE.
		}
		function removeSelection_ () {
			if (window.getSelection) { window.getSelection().removeAllRanges();	} // all browsers, except IE.
			else if (document.selection.createRange) { document.selection.empty(); } // IE.
		}
		function preventDefault_ (event) {
			if (event.preventDefault) { event.preventDefault(); }
			else { event.returnValue = false; }
		}
		panoramavr = {
			rotate: function (e) {
				var deltaX = parseInt((panoramavr._firstX - e.clientX) / panoramavr._step);
				var deltaY = parseInt((panoramavr._firstY - e.clientY) / panoramavr._step);
				panoramavr._X = panoramavr._lastX + deltaX;
				panoramavr._Y = panoramavr._lastY + deltaY;
				panoramavr._Y = Math.max(-88, Math.min(88, panoramavr._Y));
				removeSelection_();
			},
			mousemove: function(e) {
				panoramavr.rotate(e);
				preventDefault_(e);
			},
			touchmove: function(e) {
				panoramavr.rotate(e.touches[0]);
				preventDefault_(e);
			},
			mousedown: function(e) {
				panoramavr._firstX = e.clientX;
				panoramavr._firstY = e.clientY;
				addEventListener_(document, 'mousemove', panoramavr.mousemove, true);
				preventDefault_(e);
			},
			touchstart: function(e) {
				panoramavr._firstX = e.touches[0].clientX;
				panoramavr._firstY = e.touches[0].clientY;
				addEventListener_(document, 'touchmove', panoramavr.touchmove, true);
				preventDefault_(e);
			},
			mvPushMatrix: function() {
				var copy = mat4.create();
				mat4.set(this._mvMatrix, copy);
				this._mvMatrixStack.push(copy);
			},
			mvPopMatrix: function() {
				if (this._mvMatrixStack.length == 0) {
					throw "Invalid popMatrix!";
				}
				this._mvMatrix = this._mvMatrixStack.pop();
			},
			setMatrixUniforms: function() {
				var gl = this._gl;
				gl.uniformMatrix4fv(this._shaderProgram.pMatrixUniform, false, this._pMatrix);
				gl.uniformMatrix4fv(this._shaderProgram.mvMatrixUniform, false, this._mvMatrix);
				var normalMatrix = mat3.create();
				mat4.toInverseMat3(this._mvMatrix, normalMatrix);
				mat3.transpose(normalMatrix);
				gl.uniformMatrix3fv(this._shaderProgram.nMatrixUniform, false, normalMatrix);
			},
			degToRad: function(degrees) {
				return degrees * Math.PI / 180;
			},
			initGL: function (canvas) {
				try {
					this._gl = WebGLUtils.setupWebGL(canvas);
					this._gl.viewportWidth = canvas.width;
					this._gl.viewportHeight = canvas.height;
				}
				catch (e) { }
				if (!this._gl) {
					alert('Could not initialize WebGL.');
					return false;
				}
				return true;
			},
			initMatrix: function () {
				this._mvMatrix = mat4.create();
				this._mvMatrixStack = [];
				this._pMatrix = mat4.create();
			},
			getShader: function(gl, id) {
				var gl = this._gl;
				var shaderScript = document.getElementById(id);
				if (!shaderScript) {
					return null;
				}
				var str = "";
				var k = shaderScript.firstChild;
				while (k) {
					if (k.nodeType == 3) {
						str += k.textContent;
					}
					k = k.nextSibling;
				}
				var shader;
				if (shaderScript.type == "x-shader/x-fragment") {
					shader = gl.createShader(gl.FRAGMENT_SHADER);
				} else if (shaderScript.type == "x-shader/x-vertex") {
					shader = gl.createShader(gl.VERTEX_SHADER);
				} else {
					return null;
				}
				gl.shaderSource(shader, str);
				gl.compileShader(shader);
				if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
					alert(gl.getShaderInfoLog(shader));
					return null;
				}
				return shader;
			},
			initShaders: function () {
				var gl = this._gl;
				var fragmentShader = this.getShader(gl, "per-fragment-lighting-fs");
				var vertexShader = this.getShader(gl, "per-fragment-lighting-vs");
				var shaderProgram = gl.createProgram();
				gl.attachShader(shaderProgram, vertexShader);
				gl.attachShader(shaderProgram, fragmentShader);
				gl.linkProgram(shaderProgram);
				if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
					alert("Could not initialise shaders");
				}
				gl.useProgram(shaderProgram);
				shaderProgram.vertexPositionAttribute = gl.getAttribLocation(shaderProgram, "aVertexPosition");
				gl.enableVertexAttribArray(shaderProgram.vertexPositionAttribute);
				shaderProgram.vertexNormalAttribute = gl.getAttribLocation(shaderProgram, "aVertexNormal");
				gl.enableVertexAttribArray(shaderProgram.vertexNormalAttribute);
				shaderProgram.textureCoordAttribute = gl.getAttribLocation(shaderProgram, "aTextureCoord");
				gl.enableVertexAttribArray(shaderProgram.textureCoordAttribute);
				shaderProgram.pMatrixUniform = gl.getUniformLocation(shaderProgram, "uPMatrix");
				shaderProgram.mvMatrixUniform = gl.getUniformLocation(shaderProgram, "uMVMatrix");
				shaderProgram.nMatrixUniform = gl.getUniformLocation(shaderProgram, "uNMatrix");
				shaderProgram.samplerUniform = gl.getUniformLocation(shaderProgram, "uSampler");
				this._shaderProgram = shaderProgram;
			},
			handleLoadedTexture: function(texture) {
				var gl = this._gl;
				gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
				gl.bindTexture(gl.TEXTURE_2D, texture);
				gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, texture.image);
				gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
				gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
				gl.generateMipmap(gl.TEXTURE_2D);
				gl.bindTexture(gl.TEXTURE_2D, null);
			},
			initTextures: function () {
				var self = this;
				var gl = this._gl;
				this._panoramaTexture = gl.createTexture();
				this._panoramaTexture.image = new Image();
				this._panoramaTexture.image.onload = function () {
					self.handleLoadedTexture(self._panoramaTexture);
				}
				this._panoramaTexture.image.src = "images/panoramavr""" + output_extension() + """";
			},
			initSide: function (radius, height, sides) {
				var gl = this._gl;
				var vertexPositions = new Array();
				var vertexNormals = new Array();
				var vertexTextureCoords = new Array();
				for (var i = 0; i < sides + 1; ++i) {
					t = Math.PI * 2.0 / sides * i;
					vertexPositions.push(radius * Math.cos(t));	vertexPositions.push( height); vertexPositions.push(radius * Math.sin(t));
					vertexPositions.push(radius * Math.cos(t));	vertexPositions.push(-height); vertexPositions.push(radius * Math.sin(t));
					vertexNormals.push(Math.cos(t)); vertexNormals.push(0.0); vertexNormals.push(Math.sin(t));
					vertexNormals.push(Math.cos(t)); vertexNormals.push(0.0); vertexNormals.push(Math.sin(t));
					vertexTextureCoords.push(1.0 / sides * i); vertexTextureCoords.push(1.0);
					vertexTextureCoords.push(1.0 / sides * i); vertexTextureCoords.push(0.0);
				}
				var vertexNormalBuffer = gl.createBuffer();
				gl.bindBuffer(gl.ARRAY_BUFFER, vertexNormalBuffer);
				gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexNormals), gl.STATIC_DRAW);
				vertexNormalBuffer.itemSize = 3;
				vertexNormalBuffer.numItems = vertexNormals.length / 3;
				var vertexTextureCoordBuffer = gl.createBuffer();
				gl.bindBuffer(gl.ARRAY_BUFFER, vertexTextureCoordBuffer);
				gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexTextureCoords), gl.STATIC_DRAW);
				vertexTextureCoordBuffer.itemSize = 2;
				vertexTextureCoordBuffer.numItems = vertexTextureCoords.length / 2;
				var vertexPositionBuffer = gl.createBuffer();
				gl.bindBuffer(gl.ARRAY_BUFFER, vertexPositionBuffer);
				gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexPositions), gl.STATIC_DRAW);
				vertexPositionBuffer.itemSize = 3;
				vertexPositionBuffer.numItems = vertexPositions.length / 3;
				return {
					'mode':gl.TRIANGLE_STRIP,
					'vertexPositionBuffer':vertexPositionBuffer,
					'vertexNormalBuffer':vertexNormalBuffer,
					'vertexTextureCoordBuffer':vertexTextureCoordBuffer
				};
			},
			initCylinder: function (radius, height, sides) {
				var gl = this._gl;
				var glObjects = new Array();
				glObjects.push(this.initSide(radius, height, sides));
				this._glObjects = glObjects;
			},
			init: function(step) {
				var self = this;
				this._step = step;
				this._firstX = 0;
				this._firstY = 0;
				this._X = 0;
				this._Y = 0;
				this._lastX = this._X;
				this._lastY = this._Y;
				this._panorama = document.getElementById('panorama');
				if (!this.initGL(this._panorama)) return;
				this.initMatrix();
				this.initShaders();
				this.initTextures();
				this.initCylinder(1.0, 1.0, 20);
				this._gl.clearColor(1.0, 1.0, 1.0, 1.0);
				this._gl.enable(this._gl.DEPTH_TEST);
				this._loading = document.getElementById('loading');
				this._loading.innerHTML = '';
				addEventListener_(this._panorama, 'mousedown', this.mousedown, true);
				addEventListener_(this._panorama, 'touchstart', this.touchstart, true);
				addEventListener_(document, 'mouseup', function mouseup(e) {
					removeEventListener_(document, 'mousemove', self.mousemove, true);
					self._lastX = self._X;
					self._lastY = self._Y;
				}, true);
				addEventListener_(document, 'touched', function touched (e) {
					removeEventListener_(document, 'touchmove', self.touchmove, true);
					self._lastX = self._X;
					self._lastY = self._Y;
				}, true);
				this._lastTime = 0;
				this.tick();
			},
			animate: function () {
				var timeNow = new Date().getTime();
				if (this._lastTime != 0) {
					var elapsed = timeNow - this._lastTime;
				}
				this._lastTime = timeNow;
			},
			tick: function () {
				requestAnimFrame(panoramavr.tick);
				panoramavr.drawScene();
				panoramavr.animate();
			},
			drawScene: function () {
				var gl = this._gl;
				gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
				gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
				if (this._glObjects == null) {
					return;
				}
				mat4.perspective(90, gl.viewportWidth / gl.viewportHeight, 0.1, 1000.0, this._pMatrix);
				mat4.identity(this._mvMatrix);
				mat4.rotate(this._mvMatrix, this.degToRad(this._X), [0, 1, 0]);
				gl.activeTexture(gl.TEXTURE0);
				gl.bindTexture(gl.TEXTURE_2D, this._panoramaTexture);
				gl.uniform1i(this._shaderProgram.samplerUniform, 0);
				var shaderProgram = this._shaderProgram;
				gl.useProgram(shaderProgram);
				var glObjects = this._glObjects;
				for (i in glObjects) {
					var glObject = glObjects[i];
					gl.bindBuffer(gl.ARRAY_BUFFER, glObject.vertexPositionBuffer);
					gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, glObject.vertexPositionBuffer.itemSize, gl.FLOAT, false, 0, 0);
					gl.bindBuffer(gl.ARRAY_BUFFER, glObject.vertexTextureCoordBuffer);
					gl.vertexAttribPointer(shaderProgram.textureCoordAttribute, glObject.vertexTextureCoordBuffer.itemSize, gl.FLOAT, false, 0, 0);
					gl.bindBuffer(gl.ARRAY_BUFFER, glObject.vertexNormalBuffer);
					gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, glObject.vertexNormalBuffer.itemSize, gl.FLOAT, false, 0, 0);
					this.setMatrixUniforms();
					gl.drawArrays(glObject.mode, 0, glObject.vertexPositionBuffer.numItems);
				}
				gl.useProgram(null);
			}
		};
		window.onload = function () {
			panoramavr.init(3);
		}
	</script>
</head>
<body>
	<header>
		<h1>HTML5 Panorama VR</h1>
	</header>
	<section id="panoramavr-main" """ + ('style="width:%dpx; height:%dpx;' % (renderinfo.view_size[0], renderinfo.view_size[1])) + """ margin:0 auto 0 auto;">
		<div id="viewer">
			<canvas id="panorama" """ + ('style="width:%dpx; height:%dpx; border:none;' % (renderinfo.view_size[0], renderinfo.view_size[1])) + """"></canvas>
			<div id="loading">Loading...</div>
		</div>
	</section>
	<section id="rendering_info">
		<p>Rendering Info</p>
		""" + version_info() + """<br>
		Total Time: """ + "%d sec." % renderinfo.total_time + """<br>
		Total Frames: """ + "%d" % renderinfo.total_frames + """<br>
		Average Time: """ + "%.2f sec." % renderinfo.average_time + """<br>
	</section>
</body>
</html>""")

def copy_file (output_path, filename):
	import shutil
	src = os.path.join(os.path.join(os.path.dirname(decode(xshade.shade().script_path)), decode('panoramavr')), filename)
	dst = os.path.join(output_path, filename)
	shutil.copy(src, dst)

if open_option_dialog():
	scene = xshade.scene()
	if settings.makefolder:
		scenename = os.path.splitext(os.path.basename(xshade.shade().active_document))[0] if xshade.shade().active_document != '' else _('untitled')
		settings.output_path = os.path.join(settings.output_path, decode(scenename))
		if not os.path.exists(settings.output_path):
			os.mkdir(settings.output_path)
	images_path = os.path.join(settings.output_path, decode('images'))
	if not os.path.exists(images_path):
		os.mkdir(images_path)
	file_path = os.path.join(images_path, decode('panoramavr' + output_extension()))
	start_rendering(scene, file_path)
	index_path = os.path.join(settings.output_path, decode('index.html'))
	write_index_html(index_path)
	copy_file(settings.output_path, decode('glMatrix-0.9.5.min.js'))
	copy_file(settings.output_path, decode('webgl-utils.js'))
	print _('done')
#else:
#	print _('canceled')
