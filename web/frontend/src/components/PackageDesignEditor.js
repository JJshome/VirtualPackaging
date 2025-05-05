import React, { useState, useEffect } from 'react';
import { designApi } from '../services/api';
import Viewer3D from './Viewer3D';
import LLMChatInterface from './LLMChatInterface';

const PackageDesignEditor = ({ projectId, designId, onSave }) => {
  const [design, setDesign] = useState(null);
  const [packageTypes, setPackageTypes] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('design'); // 'design', 'materials', 'text', 'assistant'

  // Editable design properties
  const [editableDesign, setEditableDesign] = useState({
    package_type: '',
    material: '',
    color: '',
    dimensions_mm: [0, 0, 0],
    padding_mm: 10.0,
    wall_thickness_mm: 2.0,
    has_internal_support: true
  });

  // Fetch design data
  useEffect(() => {
    if (projectId && designId) {
      fetchDesignData();
    }
  }, [projectId, designId]);

  // Fetch package types and materials
  useEffect(() => {
    fetchPackageTypes();
    fetchMaterials();
  }, []);

  const fetchDesignData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await designApi.getDesign(projectId, designId);
      setDesign(response.data);
      
      // Set editable design properties
      setEditableDesign({
        package_type: response.data.package_type,
        material: response.data.material,
        color: response.data.color || '',
        dimensions_mm: response.data.dimensions_mm || [0, 0, 0],
        padding_mm: 10.0, // Default if not provided
        wall_thickness_mm: 2.0, // Default if not provided
        has_internal_support: response.data.has_internal_support
      });
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch design data', err);
      setError('Failed to load design data. Please try again.');
      setLoading(false);
    }
  };

  const fetchPackageTypes = async () => {
    try {
      const response = await designApi.getPackageTypes();
      setPackageTypes(response.data);
    } catch (err) {
      console.error('Failed to fetch package types', err);
      // Don't set error state here to avoid blocking the main design loading
    }
  };

  const fetchMaterials = async () => {
    try {
      const response = await designApi.getMaterials();
      setMaterials(response.data);
    } catch (err) {
      console.error('Failed to fetch materials', err);
      // Don't set error state here to avoid blocking the main design loading
    }
  };

  const handleDesignChange = (property, value) => {
    setEditableDesign(prev => ({
      ...prev,
      [property]: value
    }));
  };

  const handleDimensionChange = (index, value) => {
    const newDimensions = [...editableDesign.dimensions_mm];
    newDimensions[index] = parseFloat(value);
    handleDesignChange('dimensions_mm', newDimensions);
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would update the design via API
      // For now, we just simulate a successful update
      setTimeout(() => {
        setDesign({
          ...design,
          ...editableDesign
        });
        setLoading(false);
        if (onSave) {
          onSave({
            ...design,
            ...editableDesign
          });
        }
      }, 1000);
    } catch (err) {
      console.error('Failed to save design', err);
      setError('Failed to save design changes. Please try again.');
      setLoading(false);
    }
  };

  const handleLLMSuggestionApply = (changes) => {
    // Apply the suggested changes to the editable design
    setEditableDesign(prev => ({
      ...prev,
      ...changes
    }));
  };

  // Helper function to find package type details
  const getPackageTypeDetails = (typeId) => {
    return packageTypes.find(type => type.id === typeId) || {};
  };

  // Helper function to find material details
  const getMaterialDetails = (materialId) => {
    return materials.find(material => material.id === materialId) || {};
  };

  if (loading && !design) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-600">Loading design...</span>
      </div>
    );
  }

  if (error && !design) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <h3 className="text-lg font-semibold mb-2">Error Loading Design</h3>
        <p>{error}</p>
        <button
          onClick={fetchDesignData}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex">
          <button
            onClick={() => setActiveTab('design')}
            className={`${activeTab === 'design'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            Design
          </button>
          <button
            onClick={() => setActiveTab('materials')}
            className={`${activeTab === 'materials'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            Materials
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`${activeTab === 'text'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            Text & Labels
          </button>
          <button
            onClick={() => setActiveTab('assistant')}
            className={`${activeTab === 'assistant'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
          >
            AI Assistant
          </button>
        </nav>
      </div>

      {/* Main content area */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 p-6">
        {/* 3D Preview */}
        <div className="md:col-span-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Package Preview</h3>
          <Viewer3D
            modelUrl={design?.preview_url || '/models/default_box.stl'}
            modelType="stl"
            height="400px"
            backgroundColor="#f8fafc"
            modelColor={editableDesign.color || '#3B82F6'}
            wireframe={false}
            showAxes={true}
            showGrid={true}
          />
        </div>

        {/* Edit Panel */}
        <div className="md:col-span-2">
          {activeTab === 'design' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Design Properties</h3>
              
              <div className="space-y-4">
                {/* Package Type */}
                <div>
                  <label htmlFor="package_type" className="block text-sm font-medium text-gray-700 mb-1">
                    Package Type
                  </label>
                  <select
                    id="package_type"
                    value={editableDesign.package_type}
                    onChange={(e) => handleDesignChange('package_type', e.target.value)}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option value="">Select a package type</option>
                    {packageTypes.map((type) => (
                      <option key={type.id} value={type.name}>
                        {type.name}
                      </option>
                    ))}
                  </select>
                  {editableDesign.package_type && (
                    <p className="mt-1 text-xs text-gray-500">
                      {getPackageTypeDetails(editableDesign.package_type)?.description}
                    </p>
                  )}
                </div>

                {/* Dimensions */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Dimensions (mm)
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label htmlFor="width" className="block text-xs text-gray-500 mb-1">
                        Width
                      </label>
                      <input
                        type="number"
                        id="width"
                        value={editableDesign.dimensions_mm[0]}
                        onChange={(e) => handleDimensionChange(0, e.target.value)}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label htmlFor="height" className="block text-xs text-gray-500 mb-1">
                        Height
                      </label>
                      <input
                        type="number"
                        id="height"
                        value={editableDesign.dimensions_mm[1]}
                        onChange={(e) => handleDimensionChange(1, e.target.value)}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label htmlFor="depth" className="block text-xs text-gray-500 mb-1">
                        Depth
                      </label>
                      <input
                        type="number"
                        id="depth"
                        value={editableDesign.dimensions_mm[2]}
                        onChange={(e) => handleDimensionChange(2, e.target.value)}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                  </div>
                </div>

                {/* Padding */}
                <div>
                  <label htmlFor="padding" className="block text-sm font-medium text-gray-700 mb-1">
                    Padding (mm)
                  </label>
                  <input
                    type="number"
                    id="padding"
                    value={editableDesign.padding_mm}
                    onChange={(e) => handleDesignChange('padding_mm', parseFloat(e.target.value))}
                    min="0"
                    step="0.5"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Distance between product and packaging walls
                  </p>
                </div>

                {/* Wall Thickness */}
                <div>
                  <label htmlFor="wall_thickness" className="block text-sm font-medium text-gray-700 mb-1">
                    Wall Thickness (mm)
                  </label>
                  <input
                    type="number"
                    id="wall_thickness"
                    value={editableDesign.wall_thickness_mm}
                    onChange={(e) => handleDesignChange('wall_thickness_mm', parseFloat(e.target.value))}
                    min="0.5"
                    step="0.1"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>

                {/* Internal Support */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="internal_support"
                    checked={editableDesign.has_internal_support}
                    onChange={(e) => handleDesignChange('has_internal_support', e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="internal_support" className="ml-2 block text-sm text-gray-700">
                    Include internal support structure
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'materials' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Material Properties</h3>
              
              <div className="space-y-4">
                {/* Material Type */}
                <div>
                  <label htmlFor="material" className="block text-sm font-medium text-gray-700 mb-1">
                    Material
                  </label>
                  <select
                    id="material"
                    value={editableDesign.material}
                    onChange={(e) => handleDesignChange('material', e.target.value)}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option value="">Select a material</option>
                    {materials.map((material) => (
                      <option key={material.id} value={material.name}>
                        {material.name}
                      </option>
                    ))}
                  </select>
                  {editableDesign.material && (
                    <p className="mt-1 text-xs text-gray-500">
                      {getMaterialDetails(editableDesign.material)?.description}
                    </p>
                  )}
                </div>

                {/* Color */}
                <div>
                  <label htmlFor="color" className="block text-sm font-medium text-gray-700 mb-1">
                    Color
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="color"
                      id="color"
                      value={editableDesign.color || '#3B82F6'}
                      onChange={(e) => handleDesignChange('color', e.target.value)}
                      className="h-10 w-10 border border-gray-300 rounded"
                    />
                    <input
                      type="text"
                      value={editableDesign.color || '#3B82F6'}
                      onChange={(e) => handleDesignChange('color', e.target.value)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      placeholder="e.g. #3B82F6"
                    />
                  </div>
                </div>

                {/* Material Properties */}
                <div className="border rounded-md p-4 bg-gray-50">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Material Properties</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="block text-xs text-gray-500">Strength Rating</span>
                      <span className="text-sm font-medium">
                        {getMaterialDetails(editableDesign.material)?.strength_rating || 'N/A'}/10
                      </span>
                    </div>
                    <div>
                      <span className="block text-xs text-gray-500">Weight (g/cm²)</span>
                      <span className="text-sm font-medium">
                        {getMaterialDetails(editableDesign.material)?.weight_g_per_cm2 || 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="block text-xs text-gray-500">Cost per Unit</span>
                      <span className="text-sm font-medium">
                        ${getMaterialDetails(editableDesign.material)?.cost_per_unit?.toFixed(2) || 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="block text-xs text-gray-500">Sustainable</span>
                      <span className="text-sm font-medium">
                        {getMaterialDetails(editableDesign.material)?.sustainable ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'text' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Text & Labels</h3>
              
              <div className="space-y-4">
                <p className="text-sm text-gray-500">
                  This section allows you to customize the text and labels that appear on your packaging.
                  Add product descriptions, usage instructions, safety warnings, and other required text.
                </p>
                
                {/* Text generation form would go here */}
                <div className="p-8 text-center text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
                  <p>Text customization functionality coming soon.</p>
                  <p className="mt-2 text-sm">Use the AI Assistant tab to generate package text content.</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'assistant' && (
            <div className="h-96">
              <LLMChatInterface
                designId={designId}
                projectId={projectId}
                onSuggestionApply={handleLLMSuggestionApply}
              />
            </div>
          )}

          {/* Action buttons */}
          <div className="mt-6 flex items-center justify-end space-x-4">
            <button
              type="button"
              onClick={() => setEditableDesign({
                package_type: design.package_type,
                material: design.material,
                color: design.color || '',
                dimensions_mm: design.dimensions_mm || [0, 0, 0],
                padding_mm: 10.0,
                wall_thickness_mm: 2.0,
                has_internal_support: design.has_internal_support
              })}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Reset
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PackageDesignEditor;