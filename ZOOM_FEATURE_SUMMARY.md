# XRF Y-Axis Auto-Scaling Feature

## What Was Implemented

The XRF analysis software now automatically adjusts the **Y-axis (intensity) limits** based on the data **within the current X-axis (energy) zoom window**. This solves the issue where zooming into small peaks was difficult because the Y-axis was always scaled to the full spectrum range.

## Key Features

### ✅ **Preserves Absolute Intensity Values**
- **Critical for PPM calculations**: The actual intensity values are never changed or normalized
- Y-axis still shows "Intensity (counts)" - real values, not normalized ones
- All concentration calculations remain accurate

### ✅ **Automatic Y-Scaling on Zoom**
- When you zoom into a region on the X-axis (energy), the Y-axis automatically adjusts
- Shows only the intensity range of data within the zoom window
- Makes small peaks visible even when they have very low absolute intensity

### ✅ **Works with All Plot Elements**
- Raw data, fit curves, and background lines are all considered
- Y-limits are set based on the max/min of ALL visible elements in the zoom window
- 5% padding added above and below for better visualization

### ✅ **Multiple Zoom Triggers**
- **Display Min/Max controls**: When you change the energy range spinboxes
- **Matplotlib toolbar**: Pan, zoom, and navigation tools all trigger auto-scaling
- **Spectrum browser**: When switching between spectra

## How It Works

1. **User zooms** into an energy range (either via controls or matplotlib toolbar)
2. **System identifies** all data points (raw, fit, background) within that X-range
3. **Y-limits calculated** from min/max of those data points only
4. **Plot updates** with new Y-scale while preserving absolute intensity values

## Example Use Cases

### **Case 1: Low-Intensity Peak**
- **Before**: Peak barely visible because Y-axis includes high-intensity regions elsewhere
- **After**: Zoom to peak region → Y-axis auto-scales → peak clearly visible with proper intensity scale

### **Case 2: Background Analysis**
- **Before**: Background variations hard to see due to large Y-scale from peaks
- **After**: Zoom to background-only region → Y-axis shows fine detail of background variations

### **Case 3: Fit Quality Assessment**
- **Before**: Hard to see fit quality for small peaks
- **After**: Zoom to fit region → can clearly see how well the Gaussian fits the data

## Technical Implementation

- **New method**: `update_y_limits_for_zoom()` in `PlotCanvas` class
- **Event handling**: Connected to matplotlib's `xlim_changed` event
- **Data filtering**: Uses numpy boolean masking to find data within zoom window
- **Robust fallback**: If no data in zoom window, uses full range

## Backward Compatibility

- ✅ All existing functionality preserved
- ✅ No changes to file formats or calibration
- ✅ PPM calculations unaffected
- ✅ Export and reporting functions unchanged

## Testing

A test script (`test_zoom_functionality.py`) was created to demonstrate the feature with synthetic XRF data including:
- Linear background
- Gaussian peak at 10.5 keV
- Realistic noise levels

Run the test with: `python test_zoom_functionality.py`

---

**Result**: You can now easily examine small peaks and background details while maintaining the absolute intensity scale critical for accurate concentration calculations. 