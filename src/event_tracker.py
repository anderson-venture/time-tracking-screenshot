import threading
from datetime import datetime
from pynput import keyboard, mouse
from storage_manager import StorageManager

class EventTracker:
    """Tracks keyboard and mouse events"""
    
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.keyboard_listener = None
        self.mouse_listener = None
        self.running = False
    
    def on_key_press(self, key):
        """Callback for keyboard press events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_name = str(key)
        
        event_details = {
            'action': 'key_press',
            'key': key_name,
            'time': datetime.now().strftime('%H:%M:%S')
        }
        
        self.storage_manager.log_event('keyboard', event_details)
    
    def on_click(self, x, y, button, pressed):
        """Callback for mouse click events"""
        if pressed:  # Only log on press, not release
            event_details = {
                'action': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'time': datetime.now().strftime('%H:%M:%S')
            }
            
            self.storage_manager.log_event('mouse', event_details)
    
    def start(self):
        """Start tracking events"""
        if self.running:
            return
        
        self.running = True
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()
    
    def stop(self):
        """Stop tracking events"""
        self.running = False
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        if self.mouse_listener:
            self.mouse_listener.stop()
