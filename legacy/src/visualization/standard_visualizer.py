"""
Standard Audio Visualization Implementation
标准音频可视化实现
"""

import pygame
import numpy as np
import time
from typing import Tuple, List


class StandardAudioVisualizer:
    """标准音频可视化器 - 使用常见的可视化方法"""
    
    def __init__(self, width: int = 800, height: int = 400, num_bars: int = 64):
        """
        初始化音频可视化器
        
        Args:
            width: 可视化区域宽度
            height: 可视化区域高度
            num_bars: 频谱条数量
        """
        self.width = width
        self.height = height
        self.num_bars = num_bars
        
        # Spectrum data
        self.spectrum_data = np.zeros(num_bars)
        self.peak_data = np.zeros(num_bars)  # Peak hold values
        self.fall_speed = 0.95  # Peak decay speed
        
        # Waveform data
        self.waveform_buffer = np.zeros(width)
        self.waveform_index = 0
        
        # Volume meter data
        self.volume_level = 0.0
        self.peak_volume = 0.0
        self.volume_decay = 0.98
        
        # Color settings
        self.colors = {
            'background': (10, 10, 20),
            'bars_low': (0, 255, 0),      # Green - low frequency
            'bars_mid': (255, 255, 0),    # Yellow - mid frequency
            'bars_high': (255, 0, 0),     # Red - high frequency
            'peak': (255, 255, 255),      # White - peak values
            'waveform': (0, 150, 255),    # Blue - waveform
            'volume_bar': (50, 200, 50),  # Volume bar color
            'volume_peak': (255, 100, 100), # Volume peak color
        }
        
        # Initialize fonts
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def update_spectrum(self, audio_data: np.ndarray):
        """
        更新频谱数据 - 使用标准FFT方法
        
        Args:
            audio_data: 音频数据数组
        """
        if len(audio_data) < 512:
            return
        
        # Ensure data is in float format
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # Take appropriate length data for FFT
        fft_size = min(len(audio_data), 2048)
        audio_chunk = audio_data[:fft_size]
        
        # Apply window function to reduce spectral leakage
        windowed = audio_chunk * np.hanning(len(audio_chunk))
        
        # Calculate FFT
        fft_data = np.fft.rfft(windowed)
        magnitude = np.abs(fft_data)
        
        # Convert to decibels
        magnitude = np.maximum(magnitude, 1e-10)  # Avoid log(0)
        db_data = 20 * np.log10(magnitude)
        
        # Group into spectrum bars
        frequencies_per_bar = len(db_data) // self.num_bars
        
        for i in range(self.num_bars):
            start_idx = i * frequencies_per_bar
            end_idx = (i + 1) * frequencies_per_bar
            
            if end_idx <= len(db_data):
                # 取该频段的平均值
                avg_db = np.mean(db_data[start_idx:end_idx])
                
                # 标准化到0-1范围 (假设-60dB到0dB的范围)
                normalized = (avg_db + 60) / 60
                normalized = max(0, min(1, normalized))
                
                # 平滑更新
                self.spectrum_data[i] = self.spectrum_data[i] * 0.8 + normalized * 0.2
                
                # 峰值保持
                if normalized > self.peak_data[i]:
                    self.peak_data[i] = normalized
                else:
                    self.peak_data[i] *= self.fall_speed
    
    def update_waveform(self, audio_data: np.ndarray):
        """
        更新波形数据
        
        Args:
            audio_data: 音频数据数组
        """
        if len(audio_data) == 0:
            return
        
        # 确保数据是浮点数格式
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # 下采样到显示宽度
        samples_per_pixel = max(1, len(audio_data) // self.width)
        
        for i in range(min(self.width, len(audio_data) // samples_per_pixel)):
            start_idx = i * samples_per_pixel
            end_idx = (i + 1) * samples_per_pixel
            
            # 取RMS值作为该像素的振幅
            if end_idx <= len(audio_data):
                segment = audio_data[start_idx:end_idx]
                rms = np.sqrt(np.mean(segment ** 2))
                self.waveform_buffer[i] = rms
    
    def update_volume(self, audio_data: np.ndarray):
        """
        更新音量表数据
        
        Args:
            audio_data: 音频数据数组
        """
        if len(audio_data) == 0:
            return
        
        # 确保数据是浮点数格式
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # 计算RMS音量
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # 平滑音量
        self.volume_level = self.volume_level * 0.9 + rms * 0.1
        
        # 峰值保持
        if rms > self.peak_volume:
            self.peak_volume = rms
        else:
            self.peak_volume *= self.volume_decay
    
    def update(self, audio_data: np.ndarray):
        """
        更新所有可视化数据
        
        Args:
            audio_data: 音频数据数组
        """
        self.update_spectrum(audio_data)
        self.update_waveform(audio_data)
        self.update_volume(audio_data)
    
    def draw_spectrum(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        """绘制频谱条"""
        bar_width = (width - self.num_bars) // self.num_bars
        
        for i in range(self.num_bars):
            bar_x = x + i * (bar_width + 1)
            bar_height = int(self.spectrum_data[i] * height)
            peak_height = int(self.peak_data[i] * height)
            
            # 根据频率选择颜色
            if i < self.num_bars // 3:
                color = self.colors['bars_low']
            elif i < 2 * self.num_bars // 3:
                color = self.colors['bars_mid']
            else:
                color = self.colors['bars_high']
            
            # 绘制频谱条
            if bar_height > 0:
                pygame.draw.rect(surface, color, 
                               (bar_x, y + height - bar_height, bar_width, bar_height))
            
            # 绘制峰值线
            if peak_height > bar_height + 2:
                pygame.draw.rect(surface, self.colors['peak'],
                               (bar_x, y + height - peak_height, bar_width, 2))
    
    def draw_waveform(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        """绘制波形"""
        center_y = y + height // 2
        
        points = []
        for i in range(width):
            if i < len(self.waveform_buffer):
                wave_y = center_y - int(self.waveform_buffer[i] * height // 2)
                points.append((x + i, wave_y))
        
        if len(points) > 1:
            pygame.draw.lines(surface, self.colors['waveform'], False, points, 2)
        
        # 绘制中心线
        pygame.draw.line(surface, (50, 50, 50), (x, center_y), (x + width, center_y), 1)
    
    def draw_volume_meter(self, surface: pygame.Surface, x: int, y: int, width: int, height: int):
        """绘制音量表"""
        # 背景
        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))
        pygame.draw.rect(surface, (100, 100, 100), (x, y, width, height), 2)
        
        # 音量条
        volume_width = int(self.volume_level * width)
        if volume_width > 0:
            pygame.draw.rect(surface, self.colors['volume_bar'], 
                           (x + 2, y + 2, volume_width - 4, height - 4))
        
        # 峰值标记
        peak_x = int(self.peak_volume * width)
        if peak_x > 2:
            pygame.draw.line(surface, self.colors['volume_peak'],
                           (x + peak_x, y + 2), (x + peak_x, y + height - 2), 3)
        
        # 音量文字
        volume_text = f"{self.volume_level * 100:.0f}%"
        text_surface = self.small_font.render(volume_text, True, (200, 200, 200))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(text_surface, text_rect)
    
    def draw(self, surface: pygame.Surface, x: int = 0, y: int = 0):
        """
        绘制完整的音频可视化
        
        Args:
            surface: 绘制表面
            x: X坐标
            y: Y坐标
        """
        # 计算各部分的尺寸和位置
        spectrum_height = self.height * 2 // 3
        waveform_height = self.height // 6
        volume_height = self.height // 6
        
        spectrum_y = y
        waveform_y = y + spectrum_height + 10
        volume_y = y + spectrum_height + waveform_height + 20
        
        # 绘制标题
        title_surface = self.font.render("Audio Spectrum", True, (255, 255, 255))
        surface.blit(title_surface, (x + 10, spectrum_y + 5))
        
        # 绘制频谱
        self.draw_spectrum(surface, x + 10, spectrum_y + 30, self.width - 20, spectrum_height - 40)
        
        # 绘制波形标题
        wave_title = self.small_font.render("Waveform", True, (200, 200, 200))
        surface.blit(wave_title, (x + 10, waveform_y))
        
        # 绘制波形
        self.draw_waveform(surface, x + 10, waveform_y + 20, self.width - 20, waveform_height - 20)
        
        # 绘制音量表标题
        vol_title = self.small_font.render("Volume", True, (200, 200, 200))
        surface.blit(vol_title, (x + 10, volume_y))
        
        # 绘制音量表
        self.draw_volume_meter(surface, x + 10, volume_y + 20, self.width - 20, volume_height - 20)