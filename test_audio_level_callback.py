#!/usr/bin/env python
"""Test audio level callback integration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.analyzer import MicrophoneAnalyzer
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_audio_level_callback():
    """Test that audio level callbacks work."""
    
    analyzer = MicrophoneAnalyzer()
    
    # Track received levels
    levels_received = []
    
    def audio_level_handler(data):
        """Handle audio level updates."""
        level = data.get('level', 0)
        energy = data.get('energy', 0)
        levels_received.append(level)
        logger.info(f"🔊 Audio Level: {level:.2%} | Energy: {energy:.6f}")
    
    # Register the callback
    analyzer.register_audio_level_callback(audio_level_handler)
    logger.info("✅ Callback registered")
    
    # Start analyzer
    try:
        logger.info("🎙️ Starting microphone analyzer...")
        analyzer.start()
        
        # Let it run for 5 seconds
        logger.info("Recording for 5 seconds...")
        time.sleep(5)
        
        # Stop
        logger.info("⏹️ Stopping analyzer...")
        analyzer.stop()
        
        # Check results
        if levels_received:
            logger.info(f"✅ SUCCESS: Received {len(levels_received)} audio level updates")
            logger.info(f"   Min level: {min(levels_received):.2%}")
            logger.info(f"   Max level: {max(levels_received):.2%}")
            logger.info(f"   Avg level: {sum(levels_received)/len(levels_received):.2%}")
        else:
            logger.error("❌ FAILED: No audio level updates received")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_audio_level_callback()
    sys.exit(0 if success else 1)
