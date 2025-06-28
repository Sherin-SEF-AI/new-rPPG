# Advanced rPPG (Remote Photoplethysmography) Application

A cross-platform Python application for remote heart rate monitoring using computer vision techniques. This advanced application provides real-time heart rate estimation, HRV analysis, and comprehensive signal quality assessment.

## 🌟 Features

- **Live Video Processing**: Real-time heart rate monitoring from webcam
- **File-based Processing**: Analyze pre-recorded video files
- **Advanced Face Detection**: Using MediaPipe for robust face tracking
- **Multiple rPPG Algorithms**: Chrominance, POS, and Green Channel methods
- **Signal Quality Metrics**: Comprehensive quality assessment and recommendations
- **Real-time Visualization**: Live plots of heart rate, HRV, and signal quality
- **HRV Analysis**: Time-domain, frequency-domain, and non-linear metrics
- **Cross-platform GUI**: Built with PyQt5 for Windows, Linux, and macOS
- **Data Export**: Save results to CSV/JSON formats with detailed reports

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, Linux, or macOS
- **Hardware**: Webcam (for live processing)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space

## 🚀 Quick Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/advanced-rppg.git
cd advanced-rppg

# Run the installation script
./install.sh
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/your-username/advanced-rppg.git
cd advanced-rppg

# Create virtual environment
python3 -m venv rppg_env

# Activate virtual environment
# On Linux/macOS:
source rppg_env/bin/activate
# On Windows:
rppg_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the application
pip install -e .
```

### Option 3: Using pip (if published)

```bash
pip install advanced-rppg
```

## 🎯 Usage

### Starting the Application

```bash
# Activate virtual environment (if using manual installation)
source rppg_env/bin/activate

# Run the application
python main.py

# Or use the command-line tool
rppg-app
```

### Using the Application

1. **Live Monitoring**:
   - Click "Start Live" to begin real-time heart rate monitoring
   - Position your face in the camera view
   - Ensure good lighting conditions
   - Stay relatively still for best results

2. **Video File Analysis**:
   - Click "Load Video" to select a video file
   - The application will process the video and display results

3. **Viewing Results**:
   - Real-time heart rate is displayed in the control panel
   - Signal quality metrics are shown with color-coded indicators
   - HRV metrics are calculated and displayed
   - Live plots show signal trends over time

4. **Saving Data**:
   - Use File → Save Data to export results
   - Choose between CSV and JSON formats
   - Comprehensive reports are generated automatically

## 📊 Understanding the Results

### Heart Rate Display
- **Green**: Normal range (60-100 BPM)
- **Orange**: Slightly elevated/depressed (50-60 or 100-120 BPM)
- **Red**: Outside normal range (<50 or >120 BPM)

### Signal Quality Metrics
- **Overall Quality**: Combined score of all quality factors
- **SNR**: Signal-to-Noise Ratio
- **Stability**: Signal consistency over time
- **Lighting Consistency**: Uniformity of illumination
- **Face Quality**: Face detection confidence

### HRV Metrics
- **RMSSD**: Root Mean Square of Successive Differences
- **SDNN**: Standard Deviation of NN Intervals
- **pNN50**: Percentage of successive RR intervals >50ms
- **LF/HF Ratio**: Low Frequency to High Frequency ratio

## ⚙️ Configuration

### Algorithm Selection
Choose from three rPPG algorithms:
- **Chrominance**: Advanced color-based method (default)
- **POS**: Plane-Orthogonal-to-Skin method
- **Green Channel**: Simple green channel analysis

### Processing Parameters
- **FPS**: Frame rate for processing (15-60 fps)
- **Face Landmarks**: Toggle face landmark visualization
- **Quality Metrics**: Enable/disable quality assessment

## 🔧 Troubleshooting

### Common Issues

1. **No Face Detected**:
   - Ensure face is clearly visible in camera
   - Check lighting conditions
   - Try adjusting camera position

2. **Poor Signal Quality**:
   - Improve lighting (avoid shadows and glare)
   - Reduce movement during measurement
   - Ensure consistent camera distance

3. **Application Won't Start**:
   - Check Python version (3.8+ required)
   - Verify all dependencies are installed
   - Check system requirements

4. **Camera Not Working**:
   - Ensure camera permissions are granted
   - Check if camera is being used by another application
   - Try different camera index in settings

### Performance Optimization

- **Lower FPS**: Reduce processing load for better performance
- **Smaller Window**: Process smaller video regions
- **Quality vs Speed**: Balance between accuracy and real-time performance

## 📁 Project Structure

```
advanced-rppg/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Installation script
├── install.sh             # Automated installation
├── README.md              # This file
├── rppg_core/             # Core rPPG processing
│   ├── __init__.py
│   ├── face_detector.py   # Face detection and tracking
│   ├── signal_processor.py # rPPG signal processing
│   ├── quality_metrics.py # Signal quality assessment
│   └── hrv_analyzer.py    # HRV analysis
├── gui/                   # User interface
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── video_widget.py    # Video display and processing
│   ├── plot_widget.py     # Real-time plotting
│   └── control_panel.py   # Control panel
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── file_utils.py      # File operations
└── data/                  # Data storage directory
    └── .gitkeep
```

## 🧪 Technical Details

### rPPG Algorithms

1. **Chrominance Method**:
   - Uses color space transformations
   - Combines RGB channels for optimal signal extraction
   - Most robust for varying lighting conditions

2. **POS Method**:
   - Projects signals onto plane orthogonal to skin tone
   - Reduces motion artifacts
   - Good for stationary subjects

3. **Green Channel Method**:
   - Simple green channel analysis
   - Baseline method for comparison
   - Fastest processing

### Signal Processing Pipeline

1. **Face Detection**: MediaPipe-based face detection and landmark extraction
2. **ROI Selection**: Forehead region extraction for signal processing
3. **Signal Extraction**: RGB signal extraction from ROI
4. **Filtering**: Bandpass filtering (0.7-4.0 Hz)
5. **Frequency Analysis**: FFT-based heart rate estimation
6. **Quality Assessment**: Multi-factor quality evaluation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/advanced-rppg.git
cd advanced-rppg

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .

# Type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MediaPipe**: Face detection and landmark extraction
- **OpenCV**: Computer vision processing
- **PyQt5**: Cross-platform GUI framework
- **SciPy**: Signal processing algorithms
- **NumPy**: Numerical computing


## 🔬 Research Applications

This application is suitable for:
- **Clinical Research**: Heart rate monitoring studies
- **Sports Science**: Exercise physiology research
- **Human-Computer Interaction**: Stress detection
- **Telemedicine**: Remote health monitoring
- **Wearable Technology**: Validation studies

---

**Note**: This application is for research and educational purposes. It is not intended for medical diagnosis or treatment. Always consult healthcare professionals for medical concerns. 
