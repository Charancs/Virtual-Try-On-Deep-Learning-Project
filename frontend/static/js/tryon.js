/**
 * Virtual Try-On Application JavaScript
 * Main application logic for real-time virtual try-on
 */

class VirtualTryOnApp {
    constructor() {
        this.socket = null;
        this.videoElement = null;
        this.canvas = null;
        this.ctx = null;
        this.isProcessing = false;
        this.currentMeasurements = {};
        this.selectedClothingItem = null;
        this.poseDetectionActive = false;
        
        this.init();
    }
    
    init() {
        // Initialize DOM elements
        this.videoElement = document.getElementById('videoElement');
        this.canvas = document.getElementById('overlayCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Initialize Socket.IO connection
        this.initSocket();
        
        // Bind event listeners
        this.bindEvents();
        
        // Load initial data
        this.loadQuickClothingItems();
        
        console.log('Virtual Try-On App initialized');
    }
    
    initSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        this.socket.on('pose_detected', (data) => {
            this.handlePoseDetection(data);
        });
        
        this.socket.on('size_estimated', (data) => {
            this.handleSizeEstimation(data);
        });
        
        this.socket.on('tryon_result', (data) => {
            this.handleTryOnResult(data);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
    }
    
    bindEvents() {
        // Camera controls
        document.getElementById('startCamera').addEventListener('click', () => this.startCamera());
        document.getElementById('stopCamera').addEventListener('click', () => this.stopCamera());
        
        // Capture and save
        document.getElementById('capturePhoto').addEventListener('click', () => this.capturePhoto());
        document.getElementById('saveToWishlist').addEventListener('click', () => this.saveToWishlist());
        document.getElementById('toggle3DView').addEventListener('click', () => this.toggle3DView());
        
        // Control settings
        document.getElementById('enablePoseDetection').addEventListener('change', (e) => {
            this.poseDetectionActive = e.target.checked;
        });
        
        document.getElementById('confidenceThreshold').addEventListener('input', (e) => {
            document.getElementById('confidenceValue').textContent = e.target.value;
        });
        
        document.getElementById('overlayOpacity').addEventListener('input', (e) => {
            document.getElementById('opacityValue').textContent = e.target.value;
        });
        
        // Clothing item selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.clothing-item')) {
                const item = e.target.closest('.clothing-item');
                this.selectClothingItem(item.dataset.itemId);
            }
        });
        
        // Form submissions
        document.getElementById('loginForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        
        document.getElementById('registerForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
    }
    
    async startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: 640,
                    height: 480,
                    facingMode: 'user'
                }
            });
            
            this.videoElement.srcObject = stream;
            
            // Enable controls
            document.getElementById('startCamera').disabled = true;
            document.getElementById('stopCamera').disabled = false;
            document.getElementById('capturePhoto').disabled = false;
            document.getElementById('saveToWishlist').disabled = false;
            document.getElementById('toggle3DView').disabled = false;
            
            // Start pose detection loop
            this.startPoseDetection();
            
            console.log('Camera started successfully');
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showAlert('Camera access denied. Please check your permissions.', 'error');
        }
    }
    
    stopCamera() {
        if (this.videoElement.srcObject) {
            const tracks = this.videoElement.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            this.videoElement.srcObject = null;
        }
        
        // Disable controls
        document.getElementById('startCamera').disabled = false;
        document.getElementById('stopCamera').disabled = true;
        document.getElementById('capturePhoto').disabled = true;
        document.getElementById('saveToWishlist').disabled = true;
        document.getElementById('toggle3DView').disabled = true;
        
        // Stop pose detection
        this.poseDetectionActive = false;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        console.log('Camera stopped');
    }
    
    startPoseDetection() {
        if (!this.poseDetectionActive) {
            this.poseDetectionActive = true;
        }
        
        const detectPose = () => {
            if (this.poseDetectionActive && !this.isProcessing) {
                this.captureFrameForPoseDetection();
            }
            
            if (this.poseDetectionActive) {
                setTimeout(detectPose, 100); // 10 FPS
            }
        };
        
        detectPose();
    }
    
    captureFrameForPoseDetection() {
        if (!this.videoElement.videoWidth || !this.videoElement.videoHeight) {
            return;
        }
        
        // Create a temporary canvas to capture the frame
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.videoElement.videoWidth;
        tempCanvas.height = this.videoElement.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Draw the current video frame
        tempCtx.drawImage(this.videoElement, 0, 0);
        
        // Convert to base64
        const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
        
        // Send to server for pose detection
        this.socket.emit('detect_pose', {
            image: imageData,
            confidence_threshold: document.getElementById('confidenceThreshold').value
        });
        
        this.isProcessing = true;
    }
    
    handlePoseDetection(data) {
        this.isProcessing = false;
        
        if (data.success && data.landmarks) {
            // Clear previous drawings
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Draw pose landmarks
            this.drawPoseLandmarks(data.landmarks);
            
            // Update measurements if available
            if (data.measurements) {
                this.updateMeasurements(data.measurements);
                
                // Request size estimation if enabled
                if (document.getElementById('enableSizeEstimation').checked) {
                    this.requestSizeEstimation(data.measurements);
                }
            }
        }
    }
    
    drawPoseLandmarks(landmarks) {
        // Set drawing style
        this.ctx.fillStyle = '#ff4757';
        this.ctx.strokeStyle = '#2f3542';
        this.ctx.lineWidth = 2;
        
        // Draw landmarks as circles
        landmarks.forEach(landmark => {
            if (landmark.visibility > 0.5) {
                const x = landmark.x * this.canvas.width;
                const y = landmark.y * this.canvas.height;
                
                this.ctx.beginPath();
                this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
                this.ctx.fill();
                this.ctx.stroke();
            }
        });
        
        // Draw connections between landmarks
        this.drawPoseConnections(landmarks);
    }
    
    drawPoseConnections(landmarks) {
        // Define pose connections (simplified version)
        const connections = [
            [11, 12], // shoulders
            [11, 13], [13, 15], // left arm
            [12, 14], [14, 16], // right arm
            [11, 23], [12, 24], // torso
            [23, 24], // hips
            [23, 25], [25, 27], // left leg
            [24, 26], [26, 28], // right leg
        ];
        
        this.ctx.strokeStyle = '#74b9ff';
        this.ctx.lineWidth = 2;
        
        connections.forEach(([start, end]) => {
            if (start < landmarks.length && end < landmarks.length) {
                const startLandmark = landmarks[start];
                const endLandmark = landmarks[end];
                
                if (startLandmark.visibility > 0.5 && endLandmark.visibility > 0.5) {
                    const startX = startLandmark.x * this.canvas.width;
                    const startY = startLandmark.y * this.canvas.height;
                    const endX = endLandmark.x * this.canvas.width;
                    const endY = endLandmark.y * this.canvas.height;
                    
                    this.ctx.beginPath();
                    this.ctx.moveTo(startX, startY);
                    this.ctx.lineTo(endX, endY);
                    this.ctx.stroke();
                }
            }
        });
    }
    
    updateMeasurements(measurements) {
        this.currentMeasurements = measurements;
        
        // Update UI
        document.getElementById('shoulderWidth').textContent = 
            measurements.shoulder_width ? `${measurements.shoulder_width.toFixed(1)} px` : '--';
        document.getElementById('chestWidth').textContent = 
            measurements.chest_width ? `${measurements.chest_width.toFixed(1)} px` : '--';
        document.getElementById('waistWidth').textContent = 
            measurements.waist_width ? `${measurements.waist_width.toFixed(1)} px` : '--';
        document.getElementById('hipWidth').textContent = 
            measurements.hip_width ? `${measurements.hip_width.toFixed(1)} px` : '--';
        document.getElementById('torsoLength').textContent = 
            measurements.torso_length ? `${measurements.torso_length.toFixed(1)} px` : '--';
    }
    
    requestSizeEstimation(measurements) {
        this.socket.emit('estimate_size', {
            measurements: measurements,
            preferred_fit: document.getElementById('preferredFit').value,
            clothing_item_id: this.selectedClothingItem?.id
        });
    }
    
    handleSizeEstimation(data) {
        if (data.success) {
            // Update size recommendation
            document.getElementById('recommendedSize').textContent = data.predicted_size;
            document.getElementById('confidenceText').textContent = 
                `Confidence: ${(data.confidence * 100).toFixed(0)}%`;
            document.getElementById('confidenceBar').style.width = `${data.confidence * 100}%`;
            
            // Change color based on confidence
            const confidenceBar = document.getElementById('confidenceBar');
            if (data.confidence > 0.8) {
                confidenceBar.className = 'progress-bar bg-success';
            } else if (data.confidence > 0.6) {
                confidenceBar.className = 'progress-bar bg-warning';
            } else {
                confidenceBar.className = 'progress-bar bg-danger';
            }
        }
    }
    
    selectClothingItem(itemId) {
        // Remove previous selection
        document.querySelectorAll('.clothing-item').forEach(item => {
            item.classList.remove('border-primary', 'border-3');
        });
        
        // Add selection to clicked item
        const selectedElement = document.querySelector(`[data-item-id="${itemId}"]`);
        selectedElement.classList.add('border-primary', 'border-3');
        
        // Load item details
        this.loadClothingItemDetails(itemId);
    }
    
    async loadClothingItemDetails(itemId) {
        try {
            const response = await fetch(`/api/clothing/${itemId}`);
            const data = await response.json();
            
            if (data.success) {
                this.selectedClothingItem = data.item;
                this.updateSelectedItemDisplay(data.item);
                
                // Request virtual try-on if enabled
                if (document.getElementById('enableVirtualTryon').checked) {
                    this.requestVirtualTryOn();
                }
            }
        } catch (error) {
            console.error('Error loading clothing item:', error);
        }
    }
    
    updateSelectedItemDisplay(item) {
        const display = document.getElementById('selectedItemDisplay');
        display.innerHTML = `
            <div class="text-center">
                <img src="${item.primary_image || '/static/images/placeholder.jpg'}" 
                     alt="${item.name}" class="img-fluid mb-3" style="max-height: 200px;">
                <h6>${item.name}</h6>
                <p class="text-muted">${item.brand || 'Unknown Brand'}</p>
                <p class="fw-bold">$${item.price || '0.00'}</p>
                <div class="d-flex justify-content-center gap-2">
                    ${item.available_sizes ? item.available_sizes.map(size => 
                        `<span class="badge bg-secondary">${size}</span>`
                    ).join('') : ''}
                </div>
            </div>
        `;
    }
    
    requestVirtualTryOn() {
        if (!this.selectedClothingItem || !this.currentMeasurements) {
            return;
        }
        
        // Capture current frame
        this.captureFrameForPoseDetection();
        
        // Request virtual try-on
        this.socket.emit('virtual_tryon', {
            clothing_item_id: this.selectedClothingItem.id,
            measurements: this.currentMeasurements,
            opacity: document.getElementById('overlayOpacity').value
        });
    }
    
    handleTryOnResult(data) {
        if (data.success && data.result_image) {
            // Display result image overlay
            const img = new Image();
            img.onload = () => {
                this.ctx.globalAlpha = parseFloat(document.getElementById('overlayOpacity').value);
                this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
                this.ctx.globalAlpha = 1.0;
            };
            img.src = data.result_image;
        }
    }
    
    capturePhoto() {
        // Create a composite canvas with video and overlay
        const compositeCanvas = document.createElement('canvas');
        compositeCanvas.width = this.canvas.width;
        compositeCanvas.height = this.canvas.height;
        const compositeCtx = compositeCanvas.getContext('2d');
        
        // Draw video frame
        compositeCtx.drawImage(this.videoElement, 0, 0, compositeCanvas.width, compositeCanvas.height);
        
        // Draw overlay
        compositeCtx.drawImage(this.canvas, 0, 0);
        
        // Convert to blob and download
        compositeCanvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `virtual-tryon-${Date.now()}.jpg`;
            a.click();
            URL.revokeObjectURL(url);
        }, 'image/jpeg', 0.9);
        
        this.showAlert('Photo captured successfully!', 'success');
    }
    
    async saveToWishlist() {
        if (!this.selectedClothingItem) {
            this.showAlert('Please select a clothing item first.', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/user/wishlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    clothing_item_id: this.selectedClothingItem.id,
                    size_label: document.getElementById('recommendedSize').textContent,
                    notes: 'Saved from virtual try-on'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Item saved to wishlist!', 'success');
            } else {
                this.showAlert(data.error || 'Failed to save item', 'error');
            }
        } catch (error) {
            console.error('Error saving to wishlist:', error);
            this.showAlert('Failed to save item', 'error');
        }
    }
    
    toggle3DView() {
        const modal = new bootstrap.Modal(document.getElementById('threeDModal'));
        modal.show();
        
        // Initialize 3D viewer (placeholder)
        this.init3DViewer();
    }
    
    init3DViewer() {
        // Placeholder for 3D viewer initialization
        // This would integrate with Three.js or Unity WebGL
        const viewer = document.getElementById('threeDViewer');
        viewer.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100">
                <div class="text-center">
                    <i class="fas fa-cube fa-3x text-primary mb-3"></i>
                    <p class="text-muted">3D view will be implemented here</p>
                </div>
            </div>
        `;
    }
    
    async loadQuickClothingItems() {
        try {
            const response = await fetch('/api/clothing/featured');
            const data = await response.json();
            
            if (data.success && data.items) {
                this.renderQuickClothingItems(data.items);
            }
        } catch (error) {
            console.error('Error loading clothing items:', error);
        }
    }
    
    renderQuickClothingItems(items) {
        const grid = document.getElementById('quickClothingGrid');
        grid.innerHTML = '';
        
        items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'col-6';
            itemElement.innerHTML = `
                <div class="clothing-item border p-2" data-item-id="${item.id}">
                    <img src="${item.primary_image || '/static/images/placeholder.jpg'}" 
                         alt="${item.name}" class="img-fluid">
                    <small class="d-block text-center mt-1">${item.name}</small>
                </div>
            `;
            grid.appendChild(itemElement);
        });
    }
    
    async handleLogin() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const rememberMe = document.getElementById('rememberMe').checked;
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    remember_me: rememberMe
                })
            });
            
            const data = await response.json();
            
            if (data.success || response.ok) {
                this.showAlert('Login successful!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
                location.reload();
            } else {
                this.showAlert(data.error || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showAlert('Login failed', 'error');
        }
    }
    
    async handleRegister() {
        const firstName = document.getElementById('firstName').value;
        const lastName = document.getElementById('lastName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (password !== confirmPassword) {
            this.showAlert('Passwords do not match', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (data.success || response.ok) {
                this.showAlert('Registration successful! Please login.', 'success');
                bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
            } else {
                this.showAlert(data.error || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showAlert('Registration failed', 'error');
        }
    }
    
    showAlert(message, type = 'info') {
        // Create alert element
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        alertElement.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertElement);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.remove();
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.virtualTryOnApp = new VirtualTryOnApp();
});
