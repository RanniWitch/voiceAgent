class AudioVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            alpha: true,
            antialias: true
        });

        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.dataArray = null;
        this.bufferLength = null;

        this.sphere = null;
        this.particles = [];
        this.isListening = false;

        this.setupScene();
        this.setupLights();
        this.createSphere();
        this.createParticles();

        this.camera.position.z = 5;

        window.addEventListener('resize', () => this.onWindowResize());

        this.animate();
    }

    setupScene() {
        this.scene.fog = new THREE.Fog(0x0f0f1e, 5, 15);
    }

    setupLights() {
        const ambientLight = new THREE.AmbientLight(0x404040, 1);
        this.scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x10b981, 2, 10);
        pointLight1.position.set(2, 2, 2);
        this.scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x3b82f6, 1.5, 10);
        pointLight2.position.set(-2, -2, 2);
        this.scene.add(pointLight2);
    }

    createSphere() {
        const geometry = new THREE.IcosahedronGeometry(1.5, 4);

        const material = new THREE.MeshPhongMaterial({
            color: 0x10b981,
            emissive: 0x10b981,
            emissiveIntensity: 0.3,
            shininess: 100,
            wireframe: false,
            transparent: true,
            opacity: 0.85
        });

        this.sphere = new THREE.Mesh(geometry, material);
        this.scene.add(this.sphere);

        const wireframeMaterial = new THREE.MeshBasicMaterial({
            color: 0x10b981,
            wireframe: true,
            transparent: true,
            opacity: 0.3
        });

        this.wireframeSphere = new THREE.Mesh(geometry, wireframeMaterial);
        this.wireframeSphere.scale.set(1.02, 1.02, 1.02);
        this.scene.add(this.wireframeSphere);

        this.originalPositions = [];
        const positions = geometry.attributes.position;

        for (let i = 0; i < positions.count; i++) {
            this.originalPositions.push({
                x: positions.getX(i),
                y: positions.getY(i),
                z: positions.getZ(i)
            });
        }
    }

    createParticles() {
        const particleGeometry = new THREE.BufferGeometry();
        const particleCount = 500;
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i++) {
            positions[i] = (Math.random() - 0.5) * 20;
        }

        particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const particleMaterial = new THREE.PointsMaterial({
            color: 0x10b981,
            size: 0.05,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending
        });

        this.particleSystem = new THREE.Points(particleGeometry, particleMaterial);
        this.scene.add(this.particleSystem);
    }

    async startListening() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;

            this.microphone = this.audioContext.createMediaStreamSource(stream);
            this.microphone.connect(this.analyser);

            this.bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(this.bufferLength);

            this.isListening = true;
            return true;
        } catch (error) {
            console.error('Error accessing microphone:', error);
            return false;
        }
    }

    stopListening() {
        if (this.microphone) {
            this.microphone.disconnect();
            this.microphone = null;
        }

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }

        this.isListening = false;
    }

    updateVisualization() {
        if (!this.isListening || !this.analyser) {
            this.resetSphereToIdle();
            return;
        }

        this.analyser.getByteFrequencyData(this.dataArray);

        const average = this.dataArray.reduce((a, b) => a + b) / this.bufferLength;
        const normalizedAverage = average / 255;

        const bass = this.dataArray.slice(0, this.bufferLength / 4).reduce((a, b) => a + b) / (this.bufferLength / 4);
        const mid = this.dataArray.slice(this.bufferLength / 4, this.bufferLength / 2).reduce((a, b) => a + b) / (this.bufferLength / 4);
        const treble = this.dataArray.slice(this.bufferLength / 2).reduce((a, b) => a + b) / (this.bufferLength / 2);

        const positions = this.sphere.geometry.attributes.position;

        for (let i = 0; i < positions.count; i++) {
            const original = this.originalPositions[i];

            const frequencyIndex = Math.floor((i / positions.count) * this.bufferLength);
            const frequency = this.dataArray[frequencyIndex] / 255;

            const distortion = 1 + (frequency * 0.5 + normalizedAverage * 0.3);

            positions.setXYZ(
                i,
                original.x * distortion,
                original.y * distortion,
                original.z * distortion
            );
        }

        positions.needsUpdate = true;
        this.sphere.geometry.computeVertexNormals();

        const targetIntensity = 0.3 + normalizedAverage * 0.7;
        this.sphere.material.emissiveIntensity += (targetIntensity - this.sphere.material.emissiveIntensity) * 0.1;

        const scale = 1.02 + normalizedAverage * 0.05;
        this.wireframeSphere.scale.set(scale, scale, scale);

        const particlePositions = this.particleSystem.geometry.attributes.position;
        for (let i = 0; i < particlePositions.count; i++) {
            const x = particlePositions.getX(i);
            const y = particlePositions.getY(i);
            const z = particlePositions.getZ(i);

            const frequencyIndex = Math.floor((i / particlePositions.count) * this.bufferLength);
            const frequency = this.dataArray[frequencyIndex] / 255;

            particlePositions.setXYZ(
                i,
                x + Math.sin(Date.now() * 0.001 + i) * 0.01 * frequency,
                y + Math.cos(Date.now() * 0.001 + i) * 0.01 * frequency,
                z + Math.sin(Date.now() * 0.001 + i * 0.5) * 0.01 * frequency
            );
        }
        particlePositions.needsUpdate = true;
    }

    resetSphereToIdle() {
        const positions = this.sphere.geometry.attributes.position;

        for (let i = 0; i < positions.count; i++) {
            const original = this.originalPositions[i];
            const current = {
                x: positions.getX(i),
                y: positions.getY(i),
                z: positions.getZ(i)
            };

            positions.setXYZ(
                i,
                current.x + (original.x - current.x) * 0.05,
                current.y + (original.y - current.y) * 0.05,
                current.z + (original.z - current.z) * 0.05
            );
        }

        positions.needsUpdate = true;
        this.sphere.geometry.computeVertexNormals();

        this.sphere.material.emissiveIntensity += (0.3 - this.sphere.material.emissiveIntensity) * 0.05;

        const currentScale = this.wireframeSphere.scale.x;
        const targetScale = 1.02;
        const newScale = currentScale + (targetScale - currentScale) * 0.05;
        this.wireframeSphere.scale.set(newScale, newScale, newScale);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        this.updateVisualization();

        this.sphere.rotation.y += 0.002;
        this.wireframeSphere.rotation.y += 0.0015;
        this.wireframeSphere.rotation.x += 0.001;

        this.particleSystem.rotation.y += 0.0005;

        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
}
