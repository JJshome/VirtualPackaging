import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, useLoader } from 'react-three-fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import { OrbitControls, Environment, Grid } from '@react-three/drei';
import { Suspense } from 'react';
import * as THREE from 'three';

// Define a component for the 3D model
function Model({ url, modelType, wireframe, position, scale, color }) {
  const mesh = useRef();
  
  // Load the appropriate model based on the file extension
  let geometry;
  
  if (modelType === 'gltf' || modelType === 'glb') {
    const gltf = useLoader(GLTFLoader, url);
    return (
      <primitive 
        object={gltf.scene} 
        position={position || [0, 0, 0]} 
        scale={scale || 1} 
        ref={mesh}
      />
    );
  } else if (modelType === 'obj') {
    geometry = useLoader(OBJLoader, url);
    return (
      <primitive 
        object={geometry} 
        position={position || [0, 0, 0]} 
        scale={scale || 1} 
        ref={mesh}
      />
    );
  } else if (modelType === 'stl') {
    geometry = useLoader(STLLoader, url);
    return (
      <mesh
        ref={mesh}
        position={position || [0, 0, 0]}
        scale={scale || 1}
        geometry={geometry}
      >
        <meshStandardMaterial 
          color={color || '#3B82F6'} 
          wireframe={wireframe || false} 
          roughness={0.5} 
          metalness={0.1} 
        />
      </mesh>
    );
  } else {
    // Default fallback to a simple box for testing
    return (
      <mesh
        ref={mesh}
        position={position || [0, 0, 0]}
        scale={scale || 1}
      >
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial 
          color={color || '#3B82F6'} 
          wireframe={wireframe || false} 
          roughness={0.5} 
          metalness={0.1} 
        />
      </mesh>
    );
  }
}

// A component to rotate the camera around the model
function CameraRotator() {
  useFrame(({ camera }) => {
    camera.position.x = 5 * Math.sin(Date.now() * 0.001);
    camera.position.z = 5 * Math.cos(Date.now() * 0.001);
    camera.lookAt(0, 0, 0);
  });
  return null;
}

// Main 3D viewer component
const Viewer3D = ({
  modelUrl,
  modelType = 'stl',
  width = '100%',
  height = '500px',
  autoRotate = false,
  wireframe = false,
  backgroundColor = '#f9fafb',
  modelColor = '#3B82F6',
  showAxes = true,
  showGrid = true,
  position = [0, 0, 0],
  scale = 1,
  onLoad,
  onError
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Handle load complete
  const handleLoadComplete = () => {
    setLoading(false);
    if (onLoad) onLoad();
  };
  
  // Handle load error
  const handleLoadError = (err) => {
    setLoading(false);
    setError(err.message || 'Failed to load 3D model');
    if (onError) onError(err);
  };
  
  // Determine the appropriate loader based on file extension if not specified
  useEffect(() => {
    if (!modelType && modelUrl) {
      const extension = modelUrl.split('.').pop().toLowerCase();
      switch (extension) {
        case 'gltf':
        case 'glb':
          setModelType('gltf');
          break;
        case 'obj':
          setModelType('obj');
          break;
        case 'stl':
          setModelType('stl');
          break;
        default:
          setModelType('box'); // Fallback
      }
    }
  }, [modelUrl, modelType]);
  
  return (
    <div style={{ width, height, position: 'relative', backgroundColor }}>
      {loading && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'rgba(249, 250, 251, 0.7)',
          zIndex: 10
        }}>
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {error && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'rgba(249, 250, 251, 0.9)',
          zIndex: 10
        }}>
          <div className="text-red-500 text-center p-4">
            <div className="text-xl font-semibold mb-2">Error Loading Model</div>
            <div>{error}</div>
          </div>
        </div>
      )}
      
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        onCreated={({ gl }) => {
          gl.setClearColor(new THREE.Color(backgroundColor));
        }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight position={[-10, -10, -10]} angle={0.3} intensity={0.5} />
        
        {/* Main content */}
        <Suspense fallback={null}>
          {modelUrl && (
            <Model 
              url={modelUrl} 
              modelType={modelType} 
              wireframe={wireframe} 
              position={position} 
              scale={scale} 
              color={modelColor} 
            />
          )}
          <Environment preset="sunset" />
        </Suspense>
        
        {/* Controls and helpers */}
        <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
        {autoRotate && <CameraRotator />}
        {showGrid && <Grid args={[10, 10]} position={[0, -1, 0]} cellColor="#ddd" sectionColor="#aaa" />}
        {showAxes && <axesHelper args={[5]} />}
      </Canvas>
      
      {/* Controls overlay */}
      <div style={{
        position: 'absolute',
        bottom: '10px',
        right: '10px',
        zIndex: 20
      }}>
        <button
          className="bg-white p-2 rounded-full shadow-md hover:bg-gray-100 mr-2"
          title="Reset View"
          onClick={() => {
            // Reset camera position - would need to access the camera via a ref
            // This is a placeholder for demonstration
            console.log('Reset view');
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-700" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
          </svg>
        </button>
        <button
          className="bg-white p-2 rounded-full shadow-md hover:bg-gray-100"
          title="Toggle Wireframe"
          onClick={() => setWireframe(!wireframe)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-700" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M5 2a1 1 0 011-1h8a1 1 0 011 1v1h1a1 1 0 011 1v3a1 1 0 01-1 1H6a1 1 0 01-1-1V3a1 1 0 011-1h1V2zm3 6a1 1 0 00-1 1v6a1 1 0 001 1h4a1 1 0 001-1V9a1 1 0 00-1-1H8z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Viewer3D;