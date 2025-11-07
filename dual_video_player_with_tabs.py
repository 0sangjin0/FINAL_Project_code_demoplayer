import sys, os
import cv2
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class ResultDisplayWidget(QFrame):
    
    data_loaded = pyqtSignal()
    
    """결과 탭에 들어갈 개별 결과 표시 위젯 (제목, 불러오기 버튼, 표, 그래프, 요약)"""
    def __init__(self, title):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                color: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: #34495e;
                color: white;
                gridline-color: #2c3e50;
                alternate-background-color: #3a506b;
                border: none;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: white;
                padding: 5px;
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #2c3e50;
            }
        """)
        self.df = None

        # --- 전체 레이아웃 ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # --- 상단 (제목, 버튼) ---
        top_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.load_button = QPushButton("엑셀 파일 불러오기")
        self.load_button.clicked.connect(self.load_data)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.load_button)
        main_layout.addLayout(top_layout)

        # --- 콘텐츠 (표, 그래프) 스플리터 ---
        content_splitter = QSplitter(Qt.Vertical)
        
        # 표
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        table_font = QFont()
        table_font.setPointSize(16)
        self.table.setFont(table_font)

        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        self.table.horizontalHeader().setFont(header_font)
        
        content_splitter.addWidget(self.table)
        
        # 그래프
        plt.style.use('dark_background')
        self.figure = Figure(figsize=(8, 5))
        self.figure.tight_layout()
        self.canvas = FigureCanvas(self.figure)
        content_splitter.addWidget(self.canvas)
        
        content_splitter.setSizes([self.height() // 2, self.height() // 2])
        main_layout.addWidget(content_splitter)

    def load_data(self):
        """엑셀 파일을 불러와 표, 그래프, 그리고 요약 지표를 업데이트합니다."""
        file_name, _ = QFileDialog.getOpenFileName(self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            try:
                self.df = pd.read_excel(file_name)
                self.update_table()
                self.update_plot()
                
                self.data_loaded.emit() 
                
            except Exception as e:
                QMessageBox.warning(self, "오류", f"파일을 불러오는 중 오류가 발생했습니다:\n{e}")

    def update_table(self):
        """데이터프레임을 기반으로 표를 채웁니다."""
        if self.df is None: return
        
        self.table.setRowCount(self.df.shape[0])
        self.table.setColumnCount(self.df.shape[1])
        self.table.setHorizontalHeaderLabels(self.df.columns)
        
        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                
                item = QTableWidgetItem(str(self.df.iat[i, j]))
                item.setTextAlignment(Qt.AlignCenter) 
                self.table.setItem(i, j, item)
        
        self.table.resizeRowsToContents()

    def update_plot(self):
        """데이터프레임을 기반으로 HOTA, MOTA, IDF1의 평균값 막대 그래프를 그립니다."""
        if self.df is None: return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        metrics_to_plot = ['HOTA', 'MOTA', 'IDF1']
        plot_values = []
        valid_metric_names = []

        for metric in metrics_to_plot:
            if metric in self.df.columns and pd.api.types.is_numeric_dtype(self.df[metric]):
                mean_val = self.df[metric].mean()
                plot_values.append(mean_val)
                valid_metric_names.append(metric)

        if not valid_metric_names:
            ax.text(0.5, 0.5, "표시할 데이터가 없습니다.\n(HOTA, MOTA, IDF1 열 확인)", 
                    ha='center', va='center', color='gray', fontsize=14) 
        else:
            colors = ['#3498db', '#2ecc71', '#e74c3c']
            bars = ax.bar(valid_metric_names, plot_values, color=colors)
            ax.bar_label(bars, fmt='%.3f', fontsize=20, padding=3)

        ax.set_ylim(0.75, 1)
        
        ax.tick_params(axis='x', labelsize=20)
        ax.tick_params(axis='y', labelsize=20)

        ax.grid(True, axis='y', linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', length=0)
        
        self.figure.subplots_adjust(
            left=0.07,
            right=0.95,
            top=0.95,
            bottom=0.1
        )
        self.canvas.draw()


# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
#  메인 비디오 플레이어 애플리케이션
# =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
class DualVideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2025 숭실대 졸업작품경진대회 강동규&김상진")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet("background-color: #1d1d1d;")

        # --- 탭 위젯 설정 ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border-top: 2px solid #3c3c3c;
            }
            QTabBar::tab {
                background: #2c3e50;
                color: white;
                padding: 10px 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
            }
        """)
        self.video_tab = QWidget()
        self.results_tab = QWidget()
        self.tabs.addTab(self.video_tab, "영상 분석")
        self.tabs.addTab(self.results_tab, "성능 결과")

        # ===================================================================
        #  1. 영상 탭 UI 구성
        # ===================================================================
        self.setup_video_tab_ui()

        # ===================================================================
        #  2. 결과 탭 UI 구성
        # ===================================================================
        self.setup_results_tab_ui()

        # --- 최상위 레이아웃 설정 ---
        top_layout = QVBoxLayout(self)
        top_layout.addWidget(self.tabs)
        self.setLayout(top_layout)

        # --- 동작 관련 변수 초기화 ---
        self.initialize_variables()

    def setup_video_tab_ui(self):
        """영상 탭의 UI 요소를 설정합니다."""
        
        main_layout = QVBoxLayout(self.video_tab)
        
        # --- 시간 표시 레이블 ---
        self.time_label = QLabel("주행중 : 00시간 00분 00초")
        self.time_label.setFont(QFont("Arial", 12))
        self.time_label.setStyleSheet("color:white; background-color:transparent;")
        self.time_label.setFixedHeight(30)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        main_layout.addWidget(self.time_label) 

        # --- 영상 레이블 4개 ---
        self.video_label1_1 = QLabel("영상 1-1")
        self.video_label1_2 = QLabel("영상 1-2")
        self.video_label2_1 = QLabel("영상 2-1")
        self.video_label2_2 = QLabel("영상 2-2")
        video_labels = [self.video_label1_1, self.video_label1_2, self.video_label2_1, self.video_label2_2]
        for label in video_labels:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: #111; color: white; border-radius: 5px;")
            label.setMinimumSize(320, 180)
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # --- 모델별 영상 프레임 ---
        model1_frame = self.create_video_frame("기존", "#FF6347", self.video_label1_1, self.video_label1_2)
        model2_frame = self.create_video_frame("개선", "#3CB371", self.video_label2_1, self.video_label2_2)

        self.video_splitter = QSplitter(Qt.Vertical)
        self.video_splitter.addWidget(model1_frame)
        self.video_splitter.addWidget(model2_frame)
        main_layout.addWidget(self.video_splitter) 

        # --- 하단 컨트롤 패널 ---
        bottom_panel = self.create_bottom_controls()
        main_layout.addLayout(bottom_panel) 


    def create_video_frame(self, title, color, label1, label2):
        """모델별 영상 표시 프레임을 생성합니다."""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        layout.setContentsMargins(2, 0, 0, 0) 
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {color}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedWidth(120)
        
        video_splitter = QSplitter(Qt.Horizontal)
        video_splitter.addWidget(label1)
        video_splitter.addWidget(label2)
        video_splitter.setSizes([350, 650])

        layout.addWidget(title_label)
        layout.addWidget(video_splitter)
        return frame

    def create_bottom_controls(self):
        """영상 제어를 위한 하단 버튼 및 슬라이더를 생성합니다."""
        self.open_btn1_1 = QPushButton("영상 1-1 열기")
        self.open_btn1_2 = QPushButton("영상 1-2 열기")
        self.open_btn2_1 = QPushButton("영상 2-1 열기")
        self.open_btn2_2 = QPushButton("영상 2-2 열기")
        self.play_pause_btn = QPushButton("▶ 재생")

        buttons = [self.open_btn1_1, self.open_btn1_2, self.open_btn2_1, self.open_btn2_2, self.play_pause_btn]
        for btn in buttons:
            btn.setFont(QFont("Arial", 10))
            btn.setStyleSheet(
                "QPushButton { background-color:#555;color:white;border:1px solid #777;border-radius:5px; padding: 5px; }"
                "QPushButton:hover{background-color:#666;}"
                "QPushButton:disabled{background-color:#333; color:#888;}"
            )
            btn.setFixedHeight(40)
        
        self.play_pause_btn.setEnabled(False)

        self.open_btn1_1.clicked.connect(lambda: self.open_file("1-1"))
        self.open_btn1_2.clicked.connect(lambda: self.open_file("1-2"))
        self.open_btn2_1.clicked.connect(lambda: self.open_file("2-1"))
        self.open_btn2_2.clicked.connect(lambda: self.open_file("2-2"))
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)

        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setStyleSheet("""
            QSlider::groove:horizontal { border: 1px solid #999; height: 8px; background: #333; margin: 2px 0; border-radius: 4px; }
            QSlider::handle:horizontal { background: #3498db; border: 1px solid #5c5c5c; width: 18px; margin: -5px 0; border-radius: 9px; }
        """)
        self.seek_slider.sliderMoved.connect(self.set_video_position)
        self.seek_slider.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_btn1_1)
        button_layout.addWidget(self.open_btn1_2)
        button_layout.addWidget(self.open_btn2_1)
        button_layout.addWidget(self.open_btn2_2)
        button_layout.addStretch()
        button_layout.addWidget(self.play_pause_btn)

        full_layout = QVBoxLayout()
        full_layout.addLayout(button_layout)
        full_layout.addWidget(self.seek_slider)
        return full_layout

    def setup_results_tab_ui(self):
        """결과 탭의 UI 요소를 설정합니다."""
        self.original_model_results = ResultDisplayWidget("기존 모델 결과")
        self.improved_model_results = ResultDisplayWidget("개선 모델 결과")

        results_splitter = QSplitter(Qt.Horizontal)
        results_splitter.addWidget(self.original_model_results)
        results_splitter.addWidget(self.improved_model_results)
        
        self.comparison_summary_label = QLabel("각 모델의 엑셀 파일을 불러오세요.")
        self.comparison_summary_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.comparison_summary_label.setAlignment(Qt.AlignCenter)
        self.comparison_summary_label.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                padding: 10px;       
                border-radius: 8px;
                margin-top: 10px;
            }
        """)

        layout = QVBoxLayout(self.results_tab)
        layout.addWidget(results_splitter,1)
        layout.addWidget(self.comparison_summary_label)

        self.original_model_results.data_loaded.connect(self.update_comparison_summary)
        self.improved_model_results.data_loaded.connect(self.update_comparison_summary)

    def update_comparison_summary(self):
        """두 모델의 데이터를 비교하여 하단 요약 라벨을 업데이트합니다."""
        
        df_orig = self.original_model_results.df
        df_impr = self.improved_model_results.df

        if df_orig is None or df_impr is None:
            self.comparison_summary_label.setText("비교를 위해 두 엑셀 파일을 모두 불러오세요.")
            return

        try:
            metrics = ['HOTA', 'MOTA', 'IDF1']
            summary_texts = []

            for metric in metrics:
                if (metric in df_orig.columns and pd.api.types.is_numeric_dtype(df_orig[metric]) and
                    metric in df_impr.columns and pd.api.types.is_numeric_dtype(df_impr[metric])):
                    
                    old_val = df_orig[metric].mean()
                    new_val = df_impr[metric].mean()

                    if old_val != 0:
                        improvement = ((new_val - old_val) / abs(old_val)) * 100
                        color = "#2ecc71" if improvement >= 0 else "#e74c3c"
                        summary_texts.append(f"{metric} <span style='color:{color};'>{improvement:+.2f}%</span>")
                    elif new_val != 0:
                        summary_texts.append(f"{metric} (N/A → {new_val:.3f})")
                    else:
                        summary_texts.append(f"{metric} (0.00%)")
                else:
                    summary_texts.append(f"{metric} (데이터 없음)")
            
            final_text = "기존 모델 대비 " + ", ".join(summary_texts) + " 향상"
            self.comparison_summary_label.setText(final_text)

        except Exception as e:
            self.comparison_summary_label.setText(f"요약 계산 중 오류 발생: {e}")

    def initialize_variables(self):
        """플레이어 동작에 필요한 변수들을 초기화합니다."""
        self.caps = {'1-1': None, '1-2': None, '2-1': None, '2-2': None}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_videos)
        self.fps = 30
        self.total_frames = 0
        self.current_frame = 0
        self.is_paused = True

        # --- [수정 2: 탭 자동 전환 타이머 및 상태 변수] ---
        self.tab_switch_timer = QTimer(self)
        self.tab_switch_timer.timeout.connect(self.switch_tabs)
        self.current_tab_index = 0 # 0: 영상 탭, 1: 결과 탭
        # ---------------------------------------------

    def open_file(self, num_str):
        file_name, _ = QFileDialog.getOpenFileName(self, f"영상 {num_str} 선택", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_name:
            cap = cv2.VideoCapture(file_name)
            
            if not cap.isOpened() or cap.get(cv2.CAP_PROP_FRAME_WIDTH) == 0:
                QMessageBox.warning(self, "오류", 
                    f"영상({os.path.basename(file_name)})을 열 수 없습니다.\n\n"
                    "다음 사항을 확인해 보세요:\n"
                    "1. 파일 경로에 한글 외 다른 언어나 특수문자가 포함되어 있지 않은지\n"
                    "2. 영상 코덱이 시스템에 올바르게 설치되어 있는지 (예: FFmpeg)\n"
                    "3. 파일이 손상되지 않았는지")
                if cap.isOpened():
                    cap.release()
                return

            if self.caps.get(num_str):
                self.caps[num_str].release()
            
            self.caps[num_str] = cap
            video_labels = {
                '1-1': self.video_label1_1, '1-2': self.video_label1_2,
                '2-1': self.video_label2_1, '2-2': self.video_label2_2
            }
            video_labels[num_str].setText("")

            self.synchronize_videos()

    def synchronize_videos(self):
        """[수정] 로드된 모든 영상의 길이를 동기화하고 재생을 준비합니다."""
        self.total_frames = 0
        self.fps = 30 
        
        valid_caps = [c for c in self.caps.values() if c and c.isOpened()]
        if not valid_caps: return

        problematic_files = False
        for c in valid_caps:
            frames = c.get(cv2.CAP_PROP_FRAME_COUNT)
            current_fps = c.get(cv2.CAP_PROP_FPS)

            if frames <= 0 or current_fps <= 0:
                problematic_files = True
                frames = self.total_frames if self.total_frames > 0 else 3000
                current_fps = self.fps

            if frames > self.total_frames:
                self.total_frames = int(frames)
                self.fps = current_fps or 30
        
        # 0으로 나누기 오류 방지
        self.total_frames = max(1, self.total_frames)
        self.fps = max(1, self.fps)


        if problematic_files:
            QMessageBox.warning(self, "경고",
                "일부 영상 파일의 메타데이터(총 프레임, FPS)를 읽는 데 문제가 발생했습니다.\n"
                "재생이 원활하지 않을 수 있습니다. 다른 코덱으로 인코딩된 영상을 사용해 보세요.")


        self.current_frame = 0
        self.is_paused = True
        self.timer.stop()
        self.play_pause_btn.setText("▶ 재생")
        
        if all(c is not None for c in self.caps.values()):
            self.play_pause_btn.setEnabled(True)
            self.seek_slider.setEnabled(True)
        
        # 슬라이더 범위는 0 ~ (총 프레임 - 1)
        self.seek_slider.setRange(0, self.total_frames - 1)
        
        # [수정] 0번 프레임으로 탐색하고, 첫 프레임을 화면에 표시
        self.seek_all_videos(0) 
        self.seek_slider.setValue(0)
        self.time_label.setText("주행중 : 00시간 00분 00초")
        self.display_current_frame()


    def toggle_play_pause(self):
        if self.is_paused:
            # --- [수정 2: 탭 전환 타이머 시작] ---
            # 1. 즉시 영상 탭으로 이동
            self.tabs.setCurrentIndex(0)
            self.current_tab_index = 0
            # 2. 30초 후에 switch_tabs가 호출되도록 설정 (30000 ms)
            self.tab_switch_timer.start(30000) 
            # -----------------------------------
            
            # 기존 재생 로직
            self.timer.start(int(1000 / self.fps))
            self.play_pause_btn.setText("❚❚ 일시정지")
        else:
            # --- [수정 2: 탭 전환 타이머 정지] ---
            self.tab_switch_timer.stop()
            # -----------------------------------

            # 기존 일시정지 로직
            self.timer.stop()
            self.play_pause_btn.setText("▶ 재생")
        self.is_paused = not self.is_paused

    def play_videos(self):
        """[수정] 비디오를 재생합니다. (탐색 없이 cap.read()만 사용)"""
        
        # 재생 직전에 프레임 카운터 증가 (0 -> 1)
        self.current_frame += 1
        
        # --- [수정 1: 영상 자동 재시작 (루핑)] ---
        if self.current_frame >= self.total_frames:
            # self.current_frame = 0 # seek_all_videos가 대신 처리
            self.seek_all_videos(0) # 0번 프레임으로 탐색 (current_frame도 0으로 설정됨)
            # 재생 타이머는 멈추지 않고 계속 진행
        # ---------------------------------------

        # UI 업데이트 (현재 프레임 기준)
        self.seek_slider.blockSignals(True)
        self.seek_slider.setValue(self.current_frame)
        self.seek_slider.blockSignals(False)
        
        elapsed_time = self.current_frame / self.fps if self.fps > 0 else 0
        h, m, s = int(elapsed_time // 3600), int((elapsed_time % 3600) // 60), int(elapsed_time % 60)
        self.time_label.setText(f"주행중 : {h:02}시간 {m:02}분 {s:02}초")
        
        labels_map = {
            '1-1': self.video_label1_1, '1-2': self.video_label1_2,
            '2-1': self.video_label2_1, '2-2': self.video_label2_2
        }

        # 4개 영상에서 다음 프레임 읽기 (빠름)
        for key, cap in self.caps.items():
            if cap and cap.isOpened():
                ret, frame = cap.read() # [!!!] cap.set()이 없음 [!!!]
                if ret:
                    self.display_frame(frame, labels_map[key])

    # --- [삭제] update_video_frame 함수 ---
    # def update_video_frame(self, frame_idx):
    #     ...

    def display_frame(self, frame, label):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        q_img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img).scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
            
    def set_video_position(self, position):
        """[수정] 슬라이더 이동 시 비디오 위치를 설정합니다."""
        self.current_frame = position
        self.seek_all_videos(position) # 1. 모든 비디오를 해당 프레임으로 탐색
        
        # 2. 일시정지 상태면, 탐색한 프레임을 수동으로 표시
        if self.is_paused:
            self.seek_slider.setValue(position)
            elapsed_time = position / self.fps if self.fps > 0 else 0
            h, m, s = int(elapsed_time // 3600), int((elapsed_time % 3600) // 60), int(elapsed_time % 60)
            self.time_label.setText(f"주행중 : {h:02}시간 {m:02}분 {s:02}초")
            
            self.display_current_frame()

    # --- [신규: 수정 2] 탭 전환 로직 ---
    def switch_tabs(self):
        """[신규] 30초/10초 간격으로 영상 탭과 결과 탭을 전환합니다."""
        if self.current_tab_index == 0: # 현재 영상 탭(0) -> 결과 탭(1)으로
            self.current_tab_index = 1
            self.tabs.setCurrentIndex(1)
            self.tab_switch_timer.setInterval(8000) # 10초 뒤 전환
        else: # 현재 결과 탭(1) -> 영상 탭(0)으로
            self.current_tab_index = 0
            self.tabs.setCurrentIndex(0)
            self.tab_switch_timer.setInterval(30000) # 30초 뒤 전환
    # -----------------------------------

    def seek_all_videos(self, frame_idx):
        """[신규] 모든 비디오를 frame_idx로 탐색합니다. (읽지 않음)"""
        if frame_idx >= self.total_frames:
            frame_idx = self.total_frames - 1
        self.current_frame = frame_idx

        for key, cap in self.caps.items():
            if cap and cap.isOpened():
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

    def display_current_frame(self):
        """[신규] 모든 비디오에서 현재 프레임을 읽고 표시합니다."""
        labels_map = {
            '1-1': self.video_label1_1, '1-2': self.video_label1_2,
            '2-1': self.video_label2_1, '2-2': self.video_label2_2
        }
        for key, cap in self.caps.items():
            if cap and cap.isOpened():
                ret, frame = cap.read() # 현재 위치의 프레임을 읽음
                if ret:
                    self.display_frame(frame, labels_map[key])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = DualVideoPlayer()
    player.show()
    sys.exit(app.exec_())