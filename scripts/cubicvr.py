#
# -*- coding: utf-8 -*-
# @title \en Export Cubic VR HTML \enden
# @title \ja Cubic VR HTML エクスポート \endja
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

SCRIPT_UUID = "438D29FB-1125-4D74-8BE1-8AB594F8D466"

class Settings:
	fov_def = 60.0
	fov_max = 120.0
	fov_min = 5.0
	makefolder = True
	output_path = None
	extension = 0
settings = Settings
defaults = Settings

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
		'fov':{'ja':'画角', 'en':'Field of view'},
		'fov_def':{'ja':'初期値', 'en':'Default'},
		'fov_max':{'ja':'最大', 'en':'Max'},
		'fov_min':{'ja':'最小', 'en':'Min'},
		'make_scenename_subfolder':{'ja':'出力先フォルダにシーン名のサブフォルダを作成', 'en':'Make scene file name subfolder in the output folder.'},
		'error_output_folder_not_found':{'ja':'エラー: 出力先フォルダを指定してください.', 'en':'Error: Output folder not found.'},
		'error_invalid_fov':{'ja':'エラー: 画角の値が不正です.', 'en':'Error: Invalid field of view value.'},
		'error_import_numpy_failed':{'ja':'エラー: numpyがインストールされていません。Shadeのアップデートを行ってください.', 'en':'Error: import numpy failed.'},
		'done':{'ja':'完了', 'en':'Done'},
		'canceled':{'ja':'キャンセル', 'en':'Canceled'},
		'cubicvr_option':{'ja':'Cubic VR オプション', 'en':'Cubic VR'},
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
	# Cubicvr option
	#dialog.begin_group(_('fov'))
	#fov_def_id = dialog.append_float(_('fov_def'), '')
	#fov_max_id = dialog.append_float(_('fov_max'), '')
	#fov_min_id = dialog.append_float(_('fov_min'), '')
	#dialog.end_group()
	# Output option
	dialog.begin_group(_('output_option'))
	path_id = dialog.append_path(_('output_folder'))
	makefolder_id = dialog.append_bool(_('make_scenename_subfolder'))
	extension_id = dialog.append_selection(_('extensions'))
	dialog.end_group()
	# set_value
	if not settings.output_path: dialog.set_value(path_id, get_default_path())
	#dialog.set_value(fov_def_id, settings.fov_def)
	#dialog.set_value(fov_max_id, settings.fov_max)
	#dialog.set_value(fov_min_id, settings.fov_min)
	dialog.set_value(makefolder_id, settings.makefolder)
	dialog.set_value(extension_id, settings.extension)
	# set_default_value
	dialog.set_default_value(path_id, get_default_path())
	#dialog.set_default_value(fov_def_id, defaults.fov_def)
	#dialog.set_default_value(fov_max_id, defaults.fov_max)
	#dialog.set_default_value(fov_min_id, defaults.fov_min)
	dialog.set_default_value(makefolder_id, defaults.makefolder)
	dialog.set_default_value(extension_id, defaults.extension)
	dialog.append_default_button()
	if not dialog.ask('Cubic VR'):
		return False
	#settings.fov_def = dialog.get_value(fov_def_id)
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
	if settings.fov_min < 0 or settings.fov_def < settings.fov_min or settings.fov_max < settings.fov_min:
		print _('error_invalid_fov')
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

def vec3 (v3):
	return numpy.array(v3)

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

def start_rendering (scene, file_path):
	global renderinfo
	animation_settings = scene.animation_settings
	# レンダリング前の設定を保存.
	saved_image_size = scene.rendering.image_size
	saved_step = animation_settings.step
	saved_starting_frame = animation_settings.starting_frame
	saved_ending_frame = animation_settings.ending_frame
	saved_object_movie_mode = animation_settings.object_movie_mode
	saved_target = scene.camera.target
	saved_zoom = scene.camera.zoom
	saved_bank = scene.camera.bank
	saved_camera_mode = scene.camera.camera_mode
	saved_active_shapes = scene.active_shapes
	scene.select_all()
	try:
		eye = vec3(scene.camera.eye)
		target = vec3(scene.camera.target)
		d = distance(eye - target)
		rot = scene.camera.bank
		pos = (
			( 0, 0, 1),
			(-1, 0, 0),
			( 0, 0,-1),
			( 1, 0, 0),
			( 0, 1, 0),
			( 0,-1, 0)
		)
		total_frames = 6
		animation_settings.step = 1
		animation_settings.starting_frame = 0
		animation_settings.ending_frame = total_frames - 1
		image_size = scene.rendering.image_size
		scene.rendering.image_size = (max(image_size), max(image_size))
		renderinfo.image_size = scene.rendering.image_size
		renderinfo.start_time = time.time()
		scene.rendering.start_animation(encode(file_path))
		scene.camera.zoom = 18.0 # fov 90 deg.
		for i in range(total_frames):
			print '%(i)d / %(total_frames)d' % vars()
			scene.camera.target = tuple(eye + vec3(pos[i]) * d)
			if i == 4: scene.camera.camera_mode = 1 # Top Mode 真上、真下を向くときは上方向モード.
			if i == 5: scene.camera.bank = rot + math.pi
 			scene.rendering.render()
			scene.rendering.append_animation()
		scene.rendering.finish_animation()
		renderinfo.total_time = time.time() - renderinfo.start_time
		renderinfo.total_frames = total_frames
		renderinfo.average_time = float(renderinfo.total_time) / float(total_frames)
	finally:
		# レンダリング前の設定を復帰.
		scene.rendering.image_size = saved_image_size
		animation_settings.step = saved_step
		animation_settings.starting_frame = saved_starting_frame
		animation_settings.ending_frame = saved_ending_frame
		animation_settings.object_movie_mode = saved_object_movie_mode
		scene.camera.target = saved_target
		scene.camera.zoom = saved_zoom
		scene.camera.bank = saved_bank
		scene.camera.camera_mode = saved_camera_mode
		scene.active_shapes = saved_active_shapes

def version_info ():
	try:
		return xshade.shade().version_info
	except AttributeError:
		return 'Shade 10 (%d)' % xshade.shade().version

def write_index_html (index_path):
	width = renderinfo.image_size[0]
	height = renderinfo.image_size[1]
	depth = max(width, height) / 2 - 1
	pers = 2 * max(width, height) / 3
	f = open(index_path, "w")
	f.write("""<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<meta name="viewport" content="width=1024; maximum-scale=1.2;" />
	<meta name="generator" content=\"""" + version_info() + """\">
	<title>HTML5 Cubic VR</title>
	<style>
		#controller { """ + "position:absolute; z-index:100; width:%dpx; height:%dpx; top:0px; left:0;" % (width, height) + """}
		#viewer { """ + "position:absolute; width:%dpx; height:%dpx; overflow:hidden;" % (width, height) + """
			""" + "-webkit-perspective:%d; -webkit-transform-style:preserve-3d;" % (pers) + """
			""" + "-moz-perspective:%d; -moz-transform-style:preserve-3d;" % (pers) + """
		}
		#cube { """ + "width:%dpx; height:%dpx;" % (width, height) + """
			""" + "-webkit-transform-style:preserve-3d; -webkit-transform:translateZ(%dpx);" % (pers) + """
			""" + "-moz-transform-style:preserve-3d; -moz-transform:translateZ(%dpx);" % (pers) + """
		}
		.side { position:absolute; left:0px; top:0px;
			-webkit-backface-visibility:hidden;
			-moz-backface-visibility:hidden;
		}
		""" + "#side0 { -webkit-transform:translateZ(-%dpx); -moz-transform:translateZ(-%dpx); }" % (depth, depth) + """
		""" + "#side1 { -webkit-transform:rotateY(-90deg) translateZ(-%dpx); -moz-transform:rotateY(-90deg) translateZ(-%dpx); }" % (depth, depth) + """
		""" + "#side2 { -webkit-transform:rotateY(180deg) translateZ(-%dpx); -moz-transform:rotateY(180deg) translateZ(-%dpx); }" % (depth, depth) + """
		""" + "#side3 { -webkit-transform:rotateY( 90deg) translateZ(-%dpx); -moz-transform:rotateY( 90deg) translateZ(-%dpx); }" % (depth, depth) + """
		""" + "#side4 { -webkit-transform:rotateX(-90deg) translateZ(-%dpx); -moz-transform:rotateX(-90deg) translateZ(-%dpx); }" % (depth, depth) + """
		""" + "#side5 { -webkit-transform:rotateX( 90deg) translateZ(-%dpx); -moz-transform:rotateX( 90deg) translateZ(-%dpx); }" % (depth, depth) + """
	</style>
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
		cubicvr = {
			rotate: function (e) {
				var deltaX = parseInt((cubicvr._firstX - e.clientX) / cubicvr._step);
				var deltaY = parseInt((cubicvr._firstY - e.clientY) / cubicvr._step);
				cubicvr._X = cubicvr._lastX + deltaX;
				cubicvr._Y = cubicvr._lastY + deltaY;
				cubicvr._Y = Math.max(-88, Math.min(88, cubicvr._Y));
				""" + "cubicvr._cube.style.webkitTransform = 'translateZ(%dpx) rotateX(' + cubicvr._Y + 'deg) rotateY(' + cubicvr._X + 'deg)';" % (pers) + """
				""" + "cubicvr._cube.style.mozTransform = 'translateZ(%dpx) rotateX(' + cubicvr._Y + 'deg) rotateY(' + cubicvr._X + 'deg)';" % (pers) + """
				removeSelection_();
			},
			mousemove: function(e) {
				cubicvr.rotate(e);
				preventDefault_(e);
			},
			touchmove: function(e) {
				cubicvr.rotate(e.touches[0]);
				preventDefault_(e);
			},
			mousedown: function(e) {
				cubicvr._firstX = e.clientX;
				cubicvr._firstY = e.clientY;
				addEventListener_(document, 'mousemove', cubicvr.mousemove, true);
				preventDefault_(e);
			},
			touchstart: function(e) {
				cubicvr._firstX = e.touches[0].clientX;
				cubicvr._firstY = e.touches[0].clientY;
				addEventListener_(document, 'touchmove', cubicvr.touchmove, true);
				preventDefault_(e);
			},
			init: function(step) {
				this._step = step;
				this._firstX = 0;
				this._firstY = 0;
				this._X = 0;
				this._Y = 0;
				this._lastX = this._X;
				this._lastY = this._Y;
				this._cube = document.getElementById('cube');
				this._controller = document.getElementById('controller');
				for (var i = 0; i < 6; ++i) {
					addEventListener_(document.getElementById('side' + i), 'mousedown', this.mousedown, true);
					addEventListener_(document.getElementById('side' + i), 'touchstart', this.touchstart, true);
				}
				addEventListener_(this._controller, 'mousedown', this.mousedown, true);
				addEventListener_(document, 'mouseup', function mouseup(e) {
					removeEventListener_(document, 'mousemove', cubicvr.mousemove, true);
					cubicvr._lastX = cubicvr._X;
					cubicvr._lastY = cubicvr._Y;
				}, true);
				addEventListener_(this._controller, 'touchstart', this.touchstart, true);
				addEventListener_(document, 'touchend', function touchend (e) {
					removeEventListener_(document, 'touchmove', cubicvr.touchmove, true);
					cubicvr._lastX = cubicvr._X;
					cubicvr._lastY = cubicvr._Y;
				}, true);
				this._loading = document.getElementById('loading');
				this._loading.innerHTML = '';
			}
		};
		window.onload = function () {
			cubicvr.init(3);
		}
	</script>
</head>
<body>
	<header>
		<h1>HTML5 Cubic VR</h1>
	</header>
	<section id="cubicvr-main" style=" """ + "width:%dpx; height:%dpx; margin:0 auto 0 auto;" % (width, height)+ """ ">
		<div id="viewer">
			<div id="cube">
				<img id="side0" class="side" src="images/cubicvr0000""" + output_extension() + """"/>
				<img id="side1" class="side" src="images/cubicvr0001""" + output_extension() + """"/> 
				<img id="side2" class="side" src="images/cubicvr0002""" + output_extension() + """"/>
				<img id="side3" class="side" src="images/cubicvr0003""" + output_extension() + """"/>
				<img id="side4" class="side" src="images/cubicvr0004""" + output_extension() + """"/>
				<img id="side5" class="side" src="images/cubicvr0005""" + output_extension() + """"/>
			</div>
			<div id="controller"></div>
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
	file_path = os.path.join(images_path, decode('cubicvr' + output_extension()))
	start_rendering(scene, file_path)
	index_path = os.path.join(settings.output_path, decode('index.html'))
	write_index_html(index_path)
	print _('done')
#else:
#	print _('canceled')
