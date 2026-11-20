"""H.265 / HEVC batch converter."""
from __future__ import annotations
import shutil, sys, webbrowser
from pathlib import Path
from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QHeaderView, QLabel, QMainWindow, QMessageBox, QPushButton, QProgressBar, QSplitter, QStyle, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

APP_NAME="江西农网视频兼容性转换工具"
EXTS={".mp4",".mov",".mkv",".avi",".m4v",".ts",".mts",".webm"}
def resource(name): return Path(getattr(sys,"_MEIPASS",Path(__file__).parent))/name
def engine(): return str(resource("ffmpeg.exe")) if resource("ffmpeg.exe").exists() else shutil.which("ffmpeg")

class Window(QMainWindow):
 def __init__(self):
  super().__init__(); self.files=[]; self.index=0; self.ok=self.bad=0; self.proc=None
  self.setWindowTitle(f"{APP_NAME}  —  本工具由 caicats 开发制作"); self.resize(760,520); self.setMinimumSize(700,480); self.setAcceptDrops(True); self.setWindowIcon(QIcon(str(resource("app_icon.ico")))); self.ui()
 def showEvent(self,event):
  super().showEvent(event)
  if not getattr(self,"_centered",False):
   self._centered=True
   QTimer.singleShot(120,self.center_window)
 def center_window(self):
  screen=self.screen() or QApplication.primaryScreen()
  if not screen:return
  area=screen.availableGeometry(); frame=self.frameGeometry()
  self.move(area.x()+(area.width()-frame.width())//2,area.y()+(area.height()-frame.height())//2)
 def ui(self):
  self.setStyleSheet("QWidget{font-family:'Microsoft YaHei UI';color:#252525;background:#F4F4F4;font-size:12px} QPushButton{background:#F8F8F8;border:1px solid #C8C8C8;border-radius:2px;padding:3px 8px;min-height:18px} QPushButton:hover{background:#EAF5F4;border-color:#54AFA5} QPushButton:disabled{color:#A5A5A5;background:#F2F2F2;border-color:#D8D8D8} QPushButton#start{background:#10AFA0;color:#FFF;font-weight:600;border:1px solid #0D9D90;padding:5px 16px} QPushButton#start:hover{background:#0D998D} QFrame#toolbar{background:#F2F2F2;border-bottom:1px solid #CECECE} QFrame#sidePanel{background:#FAFAFA;border:1px solid #D7D7D7;border-radius:2px} QTableWidget{background:#FFF;border:1px solid #D0D0D0;border-radius:0;gridline-color:#E5E5E5;selection-background-color:#D8F0ED;selection-color:#202020;alternate-background-color:#FCFCFC} QHeaderView::section{background:#F6F6F6;border:0;border-right:1px solid #DEDEDE;border-bottom:1px solid #D0D0D0;padding:5px;font-weight:400;color:#222} QProgressBar{border:1px solid #C8C8C8;background:#ECECEC;border-radius:0;height:5px} QProgressBar::chunk{background:#10AFA0} QComboBox{background:#FFF;border:1px solid #C3C3C3;border-radius:2px;padding:3px 6px;min-height:18px} QComboBox:hover{border-color:#56AFA6} QComboBox:focus{border:1px solid #10AFA0}")
  root=QWidget(); self.setCentralWidget(root); box=QVBoxLayout(root); box.setContentsMargins(0,0,0,0); box.setSpacing(0)
  toolbar=QFrame(); toolbar.setObjectName("toolbar"); top=QHBoxLayout(toolbar); top.setContentsMargins(8,5,8,5); top.setSpacing(5)
  self.add=QPushButton("添加视频"); self.add.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)); self.add.clicked.connect(self.add_files); top.addWidget(self.add); add_folder=QPushButton("添加文件夹"); add_folder.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)); add_folder.clicked.connect(self.add_folder); top.addWidget(add_folder); remove=QPushButton("移除选中"); remove.clicked.connect(self.remove); top.addWidget(remove); clear=QPushButton("清空列表"); clear.clicked.connect(self.clear); top.addWidget(clear); top.addStretch(); self.count=QLabel("0 个文件"); self.count.setStyleSheet("color:#5E666D;padding:2px 3px;"); top.addWidget(self.count); box.addWidget(toolbar)
  content=QSplitter(Qt.Orientation.Horizontal); content.setChildrenCollapsible(False); content.setHandleWidth(1); box.addWidget(content,1)
  left=QWidget(); leftbox=QVBoxLayout(left); leftbox.setContentsMargins(8,8,4,7); leftbox.setSpacing(5)
  self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(["文件名","所在位置","状态"]); self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.table.setAlternatingRowColors(True); self.table.verticalHeader().setVisible(False); self.table.verticalHeader().setDefaultSectionSize(28); self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch); self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch); self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.ResizeToContents); self.table.setToolTip("可将视频文件或文件夹直接拖到此处"); leftbox.addWidget(self.table,1); hint=QLabel("可直接拖入视频文件或文件夹"); hint.setStyleSheet("font-size:11px;color:#708093"); leftbox.addWidget(hint); content.addWidget(left)
  side=QWidget(); sidebox=QVBoxLayout(side); sidebox.setContentsMargins(4,8,8,7); panel=QFrame(); panel.setObjectName("sidePanel"); settings=QVBoxLayout(panel); settings.setContentsMargins(9,9,9,9); settings.setSpacing(7); section=QLabel("转换设置"); section.setStyleSheet("font-size:13px;font-weight:600;color:#333"); settings.addWidget(section)
  qlabel=QLabel("画质"); qlabel.setStyleSheet("font-weight:600;color:#444"); settings.addWidget(qlabel); self.quality=QComboBox(); self.quality.addItems(["更清晰 · CRF 18","推荐 · CRF 20","更小 · CRF 23"]); self.quality.setCurrentIndex(1); settings.addWidget(self.quality)
  olabel=QLabel("成品保存方式"); olabel.setStyleSheet("font-weight:600;color:#444;margin-top:3px"); settings.addWidget(olabel); self.output_mode=QComboBox(); self.output_mode.addItems(["另存在原始目录下的新文件夹","放在原视频同目录","转换后替换原视频"]); self.output_mode.setCurrentIndex(2); self.output_mode.setToolTip("替换原视频只会在转换成功后执行，源文件会被删除。"); settings.addWidget(self.output_mode); warn=QLabel("替换仅在转换成功后删除原文件"); warn.setWordWrap(True); warn.setStyleSheet("font-size:10px;color:#707070;padding-top:2px"); settings.addWidget(warn); settings.addStretch(); sidebox.addWidget(panel)
  info=QFrame(); info.setStyleSheet("QFrame{background:#EAF7F5;border:1px solid #65BFB6;border-radius:3px} QLabel{background:#EAF7F5;border:0;color:#294B49} QPushButton{background:#FFF;color:#087F75;border:1px solid #75BEB7;text-align:center;padding:4px 7px} QPushButton:hover{background:#DDF2EF;border-color:#0B9E91}"); info_box=QVBoxLayout(info); info_box.setContentsMargins(12,8,9,8); info_box.setSpacing(5)
  info_title=QLabel("其他软件作品"); info_title.setStyleSheet("font-size:13px;font-weight:600;color:#333;padding:3px 0"); info_box.addWidget(info_title)
  intro=QLabel("江西设计批量化工具：一键批量各种操作，解放双手！\n\n一键填写明细表资金\n一键生成预算对比分析表\n一键出材料表前后变动工程量对比（给预算改）\n一键填写建议书资金，更新里面单价合价\n一键生成加水印（水印内容、地方自定义）\n一键提资材料表拆除表给预算做"); intro.setWordWrap(False); intro.setStyleSheet("font-size:11px;letter-spacing:-0.2px;line-height:1.3;padding:0"); info_box.addWidget(intro)
  links=QHBoxLayout(); links.setSpacing(6); download=QPushButton("其他工具下载"); download.setToolTip("https://fcai.me/jxnw"); download.clicked.connect(lambda:webbrowser.open("https://fcai.me/jxnw")); links.addWidget(download); tutorial=QPushButton("工具使用教程"); tutorial.setToolTip("https://bilibili.com/video/BV1PY7A6FE41"); tutorial.clicked.connect(lambda:webbrowser.open("https://bilibili.com/video/BV1PY7A6FE41")); links.addWidget(tutorial); info_box.addLayout(links); sidebox.addWidget(info); sidebox.addStretch(); content.addWidget(side); content.setStretchFactor(0,3); content.setStretchFactor(1,2); content.setSizes([465,275])
  footer=QFrame(); footer.setObjectName("toolbar"); bottom=QVBoxLayout(footer); bottom.setContentsMargins(8,6,8,7); bottom.setSpacing(5); self.progress=QProgressBar(); self.progress.setRange(0,100); bottom.addWidget(self.progress); foot=QHBoxLayout(); self.status=QLabel("拖入或添加视频后即可开始转换"); self.status.setStyleSheet("font-size:11px;color:#626B73"); foot.addWidget(self.status); foot.addStretch(); self.cancel=QPushButton("取消"); self.cancel.setEnabled(False); self.cancel.clicked.connect(self.stop); foot.addWidget(self.cancel); self.start=QPushButton("开始转换"); self.start.setObjectName("start"); self.start.clicked.connect(self.begin); foot.addWidget(self.start); bottom.addLayout(foot); box.addWidget(footer)
 def add_files(self):
  names,_=QFileDialog.getOpenFileNames(self,"选择视频文件","","视频文件 (*.mp4 *.mov *.mkv *.avi *.m4v *.ts *.mts *.webm)"); self.add_paths(Path(x) for x in names)
 def add_folder(self):
  folder=QFileDialog.getExistingDirectory(self,"选择包含视频的文件夹")
  if folder:self.add_paths(p for p in Path(folder).rglob("*") if p.is_file() and p.suffix.lower() in EXTS)
 def add_paths(self,paths):
  known={str(x).lower() for x in self.files}
  for p in paths:
   if p.suffix.lower() in EXTS and str(p).lower() not in known:self.files.append(p); known.add(str(p).lower())
  self.draw()
 def dragEnterEvent(self,event:QDragEnterEvent):
  if event.mimeData().hasUrls(): event.acceptProposedAction()
 def dropEvent(self,event:QDropEvent):
  paths=[]
  for url in event.mimeData().urls():
   path=Path(url.toLocalFile())
   if path.is_dir(): paths.extend(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in EXTS)
   elif path.is_file(): paths.append(path)
  self.add_paths(paths); event.acceptProposedAction()
 def draw(self):
  self.table.setRowCount(len(self.files))
  for i,p in enumerate(self.files):
   for c,v in enumerate((p.name,str(p.parent),"等待中")): self.table.setItem(i,c,QTableWidgetItem(v))
  self.count.setText(f"{len(self.files)} 个文件")
 def remove(self):
  for r in sorted({x.row() for x in self.table.selectedIndexes()},reverse=True): del self.files[r]
  self.draw()
 def clear(self): self.files=[]; self.draw()
 def begin(self):
  if not self.files: QMessageBox.information(self,APP_NAME,"请先添加至少一个视频文件。"); return
  if not engine(): QMessageBox.critical(self,APP_NAME,"未找到内置 FFmpeg，请重新下载完整程序。"); return
  if self.output_mode.currentIndex()==2:
   answer=QMessageBox.warning(self,APP_NAME,"确认替换原视频？\n\n转换成功后，原视频将被新生成的 H.264 MP4 替换，原视频无法恢复。",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
   if answer!=QMessageBox.StandardButton.Yes:return
  self.index=self.ok=self.bad=0; self.start.setEnabled(False); self.cancel.setEnabled(True); self.progress.setValue(0); self.next()
 def next(self):
  if self.index>=len(self.files): self.start.setEnabled(True); self.cancel.setEnabled(False); self.status.setText(f"转换完成：成功 {self.ok} 个，失败 {self.bad} 个。"); QMessageBox.information(self,APP_NAME,f"转换完成\n\n成功：{self.ok} 个\n失败：{self.bad} 个"); return
  s=self.files[self.index]; mode=self.output_mode.currentIndex(); out=s.parent/("H264_转换完成" if mode==0 else ""); out.mkdir(exist_ok=True)
  if mode==2: target=s.with_name(f".{s.stem}_H264_转换临时{s.suffix}")
  else:
   target=out/f"{s.stem}_H264.mp4"; n=1
   while target.exists(): target=out/f"{s.stem}_H264_{n}.mp4"; n+=1
  crf=("18","20","23")[self.quality.currentIndex()]; self.table.item(self.index,2).setText("转换中"); self.status.setText(f"正在转换：{s.name}"); self.proc=QProcess(self); self.proc.setProgram(engine()); self.proc.setArguments(["-hide_banner","-y","-i",str(s),"-map","0:v:0","-map","0:a?","-c:v","libx264","-crf",crf,"-preset","medium","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",str(target)]); self.proc.finished.connect(self.done); self.proc.start()
 def done(self,code,_):
  if self.proc is None:return
  good=code==0
  if self.output_mode.currentIndex()==2:
   source=self.files[self.index]; temp=source.with_name(f".{source.stem}_H264_转换临时{source.suffix}")
   if good:
    try: source.unlink(); temp.replace(source)
    except OSError: good=False
   elif temp.exists(): temp.unlink()
  self.table.item(self.index,2).setText("已完成" if good else "失败"); self.ok+=int(good); self.bad+=int(not good); self.index+=1; self.progress.setValue(round(self.index/len(self.files)*100)); self.proc=None; self.next()
 def stop(self):
  if self.proc:self.proc.kill();self.proc=None
  self.start.setEnabled(True);self.cancel.setEnabled(False);self.status.setText("已取消。")
if __name__=="__main__":
 app=QApplication(sys.argv); app.setApplicationName(APP_NAME); w=Window(); w.show(); sys.exit(app.exec())
