<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Virtual Try-On Deep Learning Project Instructions

This project implements a real-time virtual try-on system using pose detection, 3D modeling, and deep learning for e-commerce applications.

## Key Technologies
- **Backend**: Flask, Python 3.9+
- **Computer Vision**: MediaPipe, OpenCV, TensorFlow
- **Deep Learning**: PIFuHD (GAN), VITON Network
- **3D Rendering**: Unity3D integration
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Canvas API

## Project Structure Guidelines
- Keep pose detection code in `src/pose_detection/`
- Store deep learning models in `models/`
- Place web interface files in `frontend/`
- Database scripts go in `database/`
- Configuration files in `config/`

## Code Style
- Use Python PEP 8 standards
- Document all AI/ML functions with docstrings
- Include error handling for camera/webcam operations
- Optimize for real-time performance

## Development Notes
- Focus on modularity for pose detection, size estimation, and garment fitting
- Ensure secure user authentication and data privacy
- Implement efficient caching for 3D model generation
- Test across different lighting conditions and poses
