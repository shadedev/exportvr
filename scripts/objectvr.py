#
# -*- coding: utf-8 -*-
# @title \en Export Object VR HTML \enden
# @title \ja Object VR HTML エクスポート \endja
#

import os
import math
import time

SCRIPT_UUID = "c50b3d49-6573-447c-96d2-edcf903f6bf8"
number_of_col = 30
output_path = None

class RenderingInfo:
	start_time = 0
	total_time = 0
	total_frames = 0
	average_time = 0
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
		'number_of_col':{'ja':'水平方向の分割数', 'en':'Number of col'},
		'error_output_folder_not_found':{'ja':'エラー: 出力先フォルダを指定してください.', 'en':'Error: Output folder not found.'},
		'error_invalid_number_of_col':{'ja':'エラー: 分割数を指定してください.', 'en':'Error: Invalid number of col.'},
		'done':{'ja':'完了', 'en':'Done'},
		'canceled':{'ja':'キャンセル', 'en':'Canceled'}
	}
	lang = get_lang()
	try:
		return texts[text][lang]
	except KeyError:
		print 'Warning: Missing localized string: %(text)s (lang: %(lang)s) ' % vars()
		return text	
_ = get_text

def ask_parameter ():
	global number_of_col, output_path
	dialog = xshade.create_dialog_with_uuid(SCRIPT_UUID)
	path_id = dialog.append_path(_('output_folder'))
	col_id = dialog.append_int(_('number_of_col'), '')
	dialog.set_default_value(col_id, 30)
	dialog.append_default_button()
	if not dialog.ask('Object VR'):
		return False
	number_of_col = dialog.get_value(col_id)
	output_path = dialog.get_value(path_id)
	if not os.path.exists(output_path):
		parent = os.path.dirname(output_path)
		if not os.path.exists(parent):
			print _('error_output_folder_not_found')
			return False
		os.mkdir(output_path)
	if number_of_col <= 0:
		print _('error_invalid_number_of_col')
		return False
	return True

def start_rendering (scene, file_path):
	global renderinfo
	settings = scene.animation_settings
	saved_step = settings.step
	saved_starting_frame = settings.starting_frame
	saved_ending_frame = settings.ending_frame
	saved_object_movie_mode = settings.object_movie_mode
	saved_eye = scene.camera.eye
	try:
		total_frames = number_of_col
		rotations = number_of_col - 1
		settings.step = 1
		settings.starting_frame = 0
		settings.ending_frame = total_frames - 1
		renderinfo.start_time = time.time()
		scene.rendering.start_animation(file_path)
		rad = (2.0 * math.pi) / number_of_col
		for i in range(total_frames):
			print '%(i)d / %(total_frames)d' % vars()
 			scene.rendering.render()
			scene.rendering.append_animation()
			scene.camera.rotate_eye(rad)
		scene.rendering.finish_animation()
		renderinfo.total_time = time.time() - renderinfo.start_time
		renderinfo.total_frames = total_frames
		renderinfo.average_time = float(renderinfo.total_time) / float(total_frames)
	finally:
		settings.step = saved_step
		settings.starting_frame = saved_starting_frame
		settings.ending_frame = saved_ending_frame
		settings.object_movie_mode = saved_object_movie_mode
		scene.camera.eye = saved_eye

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
		objectvr = {
			imageName: function (name, num, ext, index) {
				m = (num + index)
				return name + m.substr(m.length - num.length) + ext;
			},
			rotate: function (e) {
				var deltaX = parseInt((objectvr._firstX - e.clientX) / objectvr._step);
				var index = objectvr._lastIndex + deltaX
				if (0 <= index) { objectvr._index = (index % objectvr._N); }
				else            { objectvr._index = (objectvr._N - 1) - ((Math.abs(index) - 1) % (objectvr._N - 1)); }		
				objectvr._img.src = objectvr.imageName(objectvr._name, objectvr._num, objectvr._ext, objectvr._index);
				window.getSelection().removeAllRanges();
			},
			mousemove: function(e) {
				objectvr.rotate(e);
			},
			touchmove: function(e) {
				objectvr.rotate(e.touches[0]);
			},
			init: function(frames, step, name, num, ext) {
				for (var i = 0; i < frames; ++i) {
					var imgObj = new Image();
					imgObj.src = this.imageName(name, num, ext, i);
				}				
				this._name = name;
				this._num = num;
				this._ext = ext;
				this._N = frames;
				this._step = step;
				this._firstX = 0;
				this._index = 0;
				this._lastIndex = 0;
				this._viewer = document.getElementById('viewer');
				this._viewer.innerHTML = '';
				this._img = document.createElement("img");
				this._img.id = 'objvr';
				this._img.src = this.imageName(name, num, ext, this._index);
				this._viewer.appendChild(this._img);
				this._img.addEventListener('mousedown', function mousedown(e) { 
					objectvr._firstX = e.clientX;
					document.addEventListener('mousemove', objectvr.mousemove, true);
					e.preventDefault();
				}, true);
				document.addEventListener('mouseup', function mouseup(e) {				
					document.removeEventListener('mousemove', objectvr.mousemove, true);
					objectvr._lastIndex = objectvr._index;
				}, true);
				this._img.addEventListener('touchstart', function touchstart (e) { 
					objectvr._firstX = e.touches[0].clientX;
					document.addEventListener('touchmove', objectvr.touchmove, true);
					e.preventDefault();
				}, true);
				document.addEventListener('touched', function touched (e) {				
					document.removeEventListener('touchmove', objectvr.touchmove, true);
					objectvr._lastIndex = objectvr._index;
				}, true);
			}
		};
		window.onload = function () {
			objectvr.init(""" + ("%d" % (number_of_col)) + """, 3, 'images/objvr', '0000', '.jpg');
		}
	</script>
</head>
<body>
	<header>
		<h1>HTML5 Object VR</h1>
	</header>
	<section id="objectvr-main" style="width:320px; margin:0 auto 0 auto;">
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

if ask_parameter():
	images_path = os.path.join(output_path, 'images')
	if not os.path.exists(images_path):
		os.mkdir(images_path)
	file_path = os.path.join(images_path, 'objvr.jpg')
	scene = xshade.scene()
	start_rendering(scene, file_path)
	index_path = os.path.join(output_path, 'index.html')
	write_index_html(index_path)
	print _('done')
else:
	print _('canceled')
