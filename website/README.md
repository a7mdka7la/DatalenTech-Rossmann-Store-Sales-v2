# Rossmann Sales Forecasting Website

A modern, responsive web interface for the Rossmann Sales Forecasting API. This website provides an intuitive way to interact with the machine learning model for sales predictions.

## Features

-  **Single Store Prediction** - Get forecasts for individual stores
-  **Batch Predictions** - Process multiple predictions at once
-  **Responsive Design** - Works on desktop, tablet, and mobile
-  **Real-time API Status** - Monitor API health and model status
-  **Model Information** - View detailed model specifications
-  **Export Results** - Download batch predictions as CSV
-  **Fast & Modern** - Built with vanilla JavaScript for optimal performance

## Screenshots

### Main Interface
![Main Interface](screenshot-main.png)

### Prediction Results
![Prediction Results](screenshot-results.png)

## Prerequisites

- Node.js (v14 or higher)
- Running Rossmann Sales Forecasting API on `http://localhost:8000`

## Quick Start

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start the web server**
   ```bash
   npm start
   ```

3. **Open your browser**
   ```
   http://localhost:3000
   ```

## Development

For development with auto-reload:

```bash
npm run dev
```

## Usage

### Single Store Prediction

1. Fill in the required fields:
   - **Store ID**: Unique identifier for the store
   - **Date**: Target prediction date
   - **Promotion**: Whether a promotion is active
   - **State Holiday**: Type of state holiday (if any)
   - **School Holiday**: Whether it's a school holiday
   - **Day of Week**: Automatically calculated or manually set

2. Click "Predict Sales" to get the forecast

### Batch Predictions

1. Click "Add Prediction" to create multiple prediction forms
2. Fill in the details for each prediction
3. Click "Run Batch Prediction" to process all at once
4. Download results as CSV if needed

## API Configuration

The website is configured to connect to the FastAPI server at `http://localhost:8000`. To change this:

1. Edit `script.js`
2. Modify the `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'http://your-api-server:port';
   ```

## Features Overview

### Real-time Status Monitoring
- **Green**: API connected and model ready
- **Yellow**: Checking connection status
- **Red**: API disconnected or model not loaded

### Input Validation
- Client-side validation for all form fields
- Automatic date calculations
- Error handling with user-friendly messages

### Results Display
- Formatted sales predictions with currency formatting
- Confidence scores as percentages
- Sortable batch results table

### Export Functionality
- CSV download for batch predictions
- Includes all prediction data and metadata

## File Structure

```
website/
├── index.html          # Main HTML file
├── styles.css          # CSS styles and responsive design
├── script.js           # JavaScript functionality
├── server.js           # Express server for hosting
├── package.json        # Node.js dependencies
└── README.md          # This file
```

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## API Endpoints Used

The website interacts with these API endpoints:

- `GET /health` - API health check
- `GET /model/info` - Model information
- `POST /predict/simple` - Single predictions
- `POST /predict/batch/simple` - Batch predictions

## Keyboard Shortcuts

- **Ctrl + Enter**: Submit single prediction form
- **Escape**: Close error modals

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure the FastAPI server is running on `http://localhost:8000`
   - Check if the model files are properly loaded
   - Verify CORS is enabled on the API

2. **Prediction Errors**
   - Validate all required fields are filled
   - Check date format (YYYY-MM-DD)
   - Ensure Store ID is a positive integer

3. **Model Not Loaded**
   - Verify `rossmann_random_forest_model.pkl` exists
   - Check `feature_scaler.pkl` is in the correct location
   - Review API server logs for loading errors

### Network Issues

If you're running the API on a different host/port:

1. Update `API_BASE_URL` in `script.js`
2. Ensure CORS is properly configured on the API
3. Check firewall settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Check the API documentation at `http://localhost:8000/docs`
- Review the browser console for error messages
- Ensure all dependencies are properly installed
