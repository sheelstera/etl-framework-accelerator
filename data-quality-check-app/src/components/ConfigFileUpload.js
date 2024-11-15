import React, { useState } from 'react';
import { Button, Typography, Box } from '@mui/material';
import axios from 'axios';

function ConfigFileUpload({ onConfigUploaded }) {
    const [sourceAliases, setSourceAliases] = useState([]);

    const handleConfigUpload = async (event) => {
        const configFile = event.target.files[0];
        const formData = new FormData();
        formData.append("yaml_file", configFile);

        const response = await axios.post(`${process.env.REACT_APP_API_URL}/upload_config`, formData);
        setSourceAliases(response.data.source_aliases || []);
        onConfigUploaded(response.data.source_aliases); // Pass aliases to parent component
    };

    return (
        <Box textAlign="center">
            <Typography variant="h6">Upload Config YAML</Typography>
            <input type="file" onChange={handleConfigUpload} />
            {sourceAliases.length > 0 && (
                <Typography variant="body1" mt={2}>Data sources identified: {sourceAliases.join(', ')}</Typography>
            )}
        </Box>
    );
}

export default ConfigFileUpload;
