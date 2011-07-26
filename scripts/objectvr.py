#
# -*- coding: utf-8 -*-
# @title \en Export Object VR HTML \enden
# @title \ja Object VR HTML エクスポート \endja
# @description \en \enden
# @description \ja \endja
# @version 0.3.2
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
	number_of_col = 30
	number_of_row = 19
	render_hemisphere = False
	makefolder = False
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
		'number_of_col':{'ja':'水平方向の分割数', 'en':'Number of columns (Pan)'},
		'number_of_row':{'ja':'垂直方向の分割数', 'en':'Number of rows (Tilt)'},
		'render_hemisphere':{'ja':'上半球のみレンダリング', 'en':'Render top hemisphere only'},
		'make_scenename_subfolder':{'ja':'出力先フォルダにシーン名のサブフォルダを作成', 'en':'Make scene file name subfolder in the output folder.'},
		'error_output_folder_not_found':{'ja':'エラー: 出力先フォルダを指定してください.', 'en':'Error: Output folder not found.'},
		'error_invalid_number_of_col':{'ja':'エラー: 分割数を指定してください.', 'en':'Error: Invalid number of col.'},
		'error_import_numpy_failed':{'ja':'エラー: numpyがインストールされていません。Shadeのアップデートを行ってください.', 'en':'Error: import numpy failed.'},
		'done':{'ja':'完了', 'en':'Done'},
		'canceled':{'ja':'キャンセル', 'en':'Canceled'},
		'objectvr_option':{'ja':'Object VR オプション', 'en':'Object VR'},
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
	# Objectvr option
	dialog.begin_group(_('objectvr_option'))
	col_id = dialog.append_int(_('number_of_col'), '')
	row_id = dialog.append_int(_('number_of_row'), '')
	hemisphere_id = dialog.append_bool(_('render_hemisphere'))
	dialog.end_group()
	# Output option
	dialog.begin_group(_('output_option'))
	path_id = dialog.append_path(_('output_folder'))
	makefolder_id = dialog.append_bool(_('make_scenename_subfolder'))
	extension_id = dialog.append_selection(_('extensions'))
	dialog.end_group()
	# set_value
	if settings.output_path == None: dialog.set_value(path_id, get_default_path())
	dialog.set_value(col_id, settings.number_of_col)
	dialog.set_value(row_id, settings.number_of_row)
	dialog.set_value(hemisphere_id, settings.render_hemisphere)
	dialog.set_value(makefolder_id, settings.makefolder)
	dialog.set_value(extension_id, settings.extension)
	# set_default_value
	dialog.set_default_value(path_id, get_default_path())
	dialog.set_default_value(col_id, defaults.number_of_col)
	dialog.set_default_value(row_id, defaults.number_of_row)
	dialog.set_default_value(hemisphere_id, defaults.render_hemisphere)
	dialog.set_default_value(makefolder_id, defaults.makefolder)
	dialog.set_default_value(extension_id, defaults.extension)
	dialog.append_default_button()
	if not dialog.ask('Object VR'):
		return False
	settings.number_of_col = dialog.get_value(col_id)
	settings.number_of_row = dialog.get_value(row_id)
	settings.render_hemisphere = dialog.get_value(hemisphere_id)
	settings.output_path = decode(dialog.get_value(path_id))
	settings.makefolder = dialog.get_value(makefolder_id)
	settings.extension = dialog.get_value(extension_id)
	if not os.path.exists(settings.output_path):
		parent = os.path.dirname(settings.output_path)
		if not os.path.exists(parent):
			print _('error_output_folder_not_found')
			return False
		os.mkdir(settings.output_path)
	if settings.number_of_col <= 0:
		print _('error_invalid_number_of_col')
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

def start_rendering (scene, file_path):
	global renderinfo
	renderinfo.image_size = scene.rendering.image_size
	animation_settings = scene.animation_settings
	# レンダリング前の設定を保存.
	saved_step = animation_settings.step
	saved_starting_frame = animation_settings.starting_frame
	saved_ending_frame = animation_settings.ending_frame
	saved_object_movie_mode = animation_settings.object_movie_mode
	saved_eye = scene.camera.eye
	saved_active_shapes = scene.active_shapes
	scene.select_all()
	saved_sequence_value = scene.sequence_value
	try:
		total_frames = settings.number_of_row * settings.number_of_col
		animation_settings.step = 1
		animation_settings.starting_frame = 0
		animation_settings.ending_frame = total_frames - 1
		renderinfo.start_time = time.time()
		scene.rendering.start_animation(encode(file_path))
		#rad = (2.0 * math.pi) / number_of_col
		row = (settings.number_of_row * 2 - 1) if settings.render_hemisphere else settings.number_of_row
		rotations = row * settings.number_of_col - 1
		# 視線が水平になるように視点を移動する.
		eye = vec4(scene.camera.eye)
		target = vec4(scene.camera.target)
		d = distance(eye - target) * 2.0
		eye[1] = target[1]
		eye = target + normalize(eye - target) * d
		for i in range(total_frames):
			print '%(i)d / %(total_frames)d' % vars()
			scene.sequence_value = i
			scene.camera.eye = rotate_eye(eye, target, i, rotations, row)
 			scene.rendering.render()
			scene.rendering.append_animation()
			#scene.camera.rotate_eye(rad)
		scene.rendering.finish_animation()
		renderinfo.total_time = time.time() - renderinfo.start_time
		renderinfo.total_frames = total_frames
		renderinfo.average_time = float(renderinfo.total_time) / float(total_frames)
	finally:
		# レンダリング前の設定を復帰.
		animation_settings.step = saved_step
		animation_settings.starting_frame = saved_starting_frame
		animation_settings.ending_frame = saved_ending_frame
		animation_settings.object_movie_mode = saved_object_movie_mode
		scene.camera.eye = saved_eye
		scene.active_shapes = saved_active_shapes
		scene.sequence_value = saved_sequence_value

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
	<title>HTML5 Object VR</title>
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
		objectvr = {
			imageName: function (name, num, ext, index) {
				m = (num + index)
				return name + m.substr(m.length - num.length) + ext;
			},
			rotate: function (e) {
				var deltaX = parseInt((objectvr._firstX - e.clientX) / objectvr._stepX);
				var deltaY = parseInt((objectvr._firstY - e.clientY) / objectvr._stepY);
				objectvr._X = objectvr._lastX + deltaX;
				objectvr._Y = objectvr._lastY + deltaY;
				if (0 <= objectvr._X) { objectvr._X = (objectvr._X % (objectvr._cols - 1)); }
				else                  { objectvr._X = (objectvr._cols - 1) - ((Math.abs(objectvr._X) - 1) % (objectvr._cols - 1)); }
				objectvr._Y = Math.max(Math.min(objectvr._Y, objectvr._rows - 1), 0);
				var index = objectvr._X + objectvr._Y * objectvr._cols;
				index = Math.max(Math.min(index, objectvr._N - 1), 0);
				objectvr._img.src = objectvr.imageName(objectvr._name, objectvr._num, objectvr._ext, index);
				removeSelection_();
			},
			mousemove: function(e) {
				objectvr.rotate(e);
				preventDefault_(e);
			},
			touchmove: function(e) {
				objectvr.rotate(e.touches[0]);
				preventDefault_(e);
			},
			init: function(cols, rows, stepX, stepY, name, num, ext) {
				var frames = cols * rows;
				for (var i = 0; i < frames; ++i) {
					var imgObj = new Image();
					imgObj.src = this.imageName(name, num, ext, i);
				}
				this._name = name;
				this._num = num;
				this._ext = ext;
				this._cols = cols;
				this._rows = rows;
				this._N = frames;
				this._stepX = stepX;
				this._stepY = stepY;
				this._firstX = 0;
				this._firstY = 0;
				this._X = cols - 1;
				this._Y = rows - 1;
				this._lastX = this._X;
				this._lastY = this._Y;
				this._viewer = document.getElementById('viewer');
				this._viewer.innerHTML = '';
				this._img = document.createElement("img");
				this._img.id = 'objvr';
				var index = objectvr._X + objectvr._Y * objectvr._cols;
				index = Math.max(Math.min(index, objectvr._N - 1), 0);
				this._img.src = this.imageName(name, num, ext, index);
				this._viewer.appendChild(this._img);
				addEventListener_(this._img, 'mousedown', function mousedown(e) {
					objectvr._firstX = e.clientX;
					objectvr._firstY = e.clientY;
					addEventListener_(document, 'mousemove', objectvr.mousemove, true);
					preventDefault_(e);
				}, true);
				addEventListener_(document, 'mouseup', function mouseup(e) {
					removeEventListener_(document, 'mousemove', objectvr.mousemove, true);
					objectvr._lastX = objectvr._X;
					objectvr._lastY = objectvr._Y;
				}, true);
				addEventListener_(this._img, 'touchstart', function touchstart (e) {
					objectvr._firstX = e.touches[0].clientX;
					objectvr._firstY = e.touches[0].clientY;
					addEventListener_(document, 'touchmove', objectvr.touchmove, true);
					preventDefault_(e);
				}, true);
				addEventListener_(document, 'touched', function touched (e) {
					removeEventListener_(document, 'touchmove', objectvr.touchmove, true);
					objectvr._lastX = objectvr._X;
					objectvr._lastY = objectvr._Y;
				}, true);
			}
		};
		window.onload = function () {
			objectvr.init(""" + ("%d, %d, %d, %d, 'images/objvr', '0000', '%s'" % (settings.number_of_col, settings.number_of_row, stepX(90), stepY(90), output_extension())) + """);
		}
	</script>
</head>
<body>
	<header>
		<h1>HTML5 Object VR</h1>
	</header>
	<section id="objectvr-main" style="width:""" + ('%d' % renderinfo.image_size[0]) + """px; margin:0 auto 0 auto;">
		<div id="viewer">Loading...</div>
		<section id="rendering_info">
			<p>Rendering Info</p>
			""" + version_info() + """<br>
			Total Time: """ + "%d sec." % renderinfo.total_time + """<br>
			Total Frames: """ + "%d" % renderinfo.total_frames + """<br>
			Average Time: """ + "%.2f sec." % renderinfo.average_time + """<br>
		</section>
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
	file_path = os.path.join(images_path, decode('objvr' + output_extension()))
	start_rendering(scene, file_path)
	index_path = os.path.join(settings.output_path, decode('index.html'))
	write_index_html(index_path)
	print _('done')
else:
	print _('canceled')
