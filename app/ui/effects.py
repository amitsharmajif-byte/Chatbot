"""
LocalAI Chat — Custom Paint Effects
=====================================
Lightweight Qt paint utilities for futuristic UI effects.
Uses QPainter, QTimer, and QGraphicsDropShadowEffect only.
"""

from PySide6.QtCore import Qt, QTimer, QRectF, Property
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect
import math


class PulsingDot(QWidget):
    """Animated pulsing status dot indicator.
    
    Shows online/offline status with a gentle pulse animation.
    """

    def __init__(self, color: str = "#10B981", size: int = 8, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._size = size
        self._pulse_opacity = 0.4
        self._pulse_direction = 1
        self._is_active = True

        self.setFixedSize(size + 8, size + 8)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)

    def set_active(self, active: bool, color: str = ""):
        """Set status: active (green pulse) or inactive (gray static)."""
        self._is_active = active
        if color:
            self._color = QColor(color)
        elif active:
            self._color = QColor("#10B981")
        else:
            self._color = QColor("#64748B")
        self.update()

    def _animate(self):
        if not self._is_active:
            self._pulse_opacity = 0.0
            self.update()
            return

        self._pulse_opacity += 0.025 * self._pulse_direction
        if self._pulse_opacity >= 0.5:
            self._pulse_direction = -1
        elif self._pulse_opacity <= 0.1:
            self._pulse_direction = 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = self._size / 2

        # Outer glow (pulse)
        if self._is_active and self._pulse_opacity > 0:
            glow_color = QColor(self._color)
            glow_color.setAlphaF(self._pulse_opacity)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(QRectF(
                center_x - radius - 3, center_y - radius - 3,
                (radius + 3) * 2, (radius + 3) * 2
            ))

        # Core dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._color))
        painter.drawEllipse(QRectF(
            center_x - radius, center_y - radius,
            radius * 2, radius * 2
        ))

        painter.end()


class AnimatedOrb(QWidget):
    """Subtle animated gradient orb for welcome screen background.
    
    Renders a slowly shifting radial gradient — lightweight QPainter only.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(40)

    def _animate(self):
        self._phase += 0.015
        if self._phase > 2 * math.pi:
            self._phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx = w / 2 + math.sin(self._phase) * 20
        cy = h / 2 + math.cos(self._phase * 0.7) * 15

        # Primary violet orb
        gradient = QRadialGradient(cx, cy, min(w, h) * 0.35)
        gradient.setColorAt(0, QColor(124, 58, 237, 30))
        gradient.setColorAt(0.4, QColor(99, 102, 241, 15))
        gradient.setColorAt(1, QColor(8, 10, 18, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QRectF(0, 0, w, h))

        # Secondary cyan orb (offset)
        cx2 = w / 2 - math.cos(self._phase * 0.5) * 30
        cy2 = h / 2 + math.sin(self._phase * 0.8) * 25
        gradient2 = QRadialGradient(cx2, cy2, min(w, h) * 0.25)
        gradient2.setColorAt(0, QColor(34, 211, 238, 12))
        gradient2.setColorAt(0.5, QColor(34, 211, 238, 5))
        gradient2.setColorAt(1, QColor(8, 10, 18, 0))

        painter.setBrush(QBrush(gradient2))
        painter.drawEllipse(QRectF(0, 0, w, h))

        painter.end()

    def stop(self):
        """Stop animation to save CPU when not visible."""
        self._timer.stop()

    def start(self):
        """Resume animation."""
        if not self._timer.isActive():
            self._timer.start(40)


class ThinkingDots(QWidget):
    """Animated thinking indicator with 3 bouncing dots."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self.setFixedHeight(32)
        self.setMinimumWidth(80)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(40)

    def _animate(self):
        self._phase += 0.12
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        base_y = self.height() / 2
        dot_radius = 3.5
        spacing = 14

        for i in range(3):
            offset_y = math.sin(self._phase + i * 0.8) * 4
            alpha = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(self._phase + i * 0.8))
            color = QColor(167, 139, 250)  # #A78BFA
            color.setAlphaF(alpha)

            x = 20 + i * spacing
            y = base_y + offset_y

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QRectF(
                x - dot_radius, y - dot_radius,
                dot_radius * 2, dot_radius * 2
            ))

        painter.end()

    def stop(self):
        self._timer.stop()

    def start(self):
        if not self._timer.isActive():
            self._timer.start(40)


def apply_glow_effect(widget: QWidget, color: str = "#7C3AED", radius: int = 20, opacity: float = 0.3):
    """Apply a subtle glow shadow effect to any widget."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(QColor(color))
    effect.setBlurRadius(radius)
    effect.setOffset(0, 0)
    # Note: QGraphicsDropShadowEffect doesn't have setOpacity
    # The alpha in the color controls the intensity
    glow_color = QColor(color)
    glow_color.setAlphaF(opacity)
    effect.setColor(glow_color)
    widget.setGraphicsEffect(effect)
