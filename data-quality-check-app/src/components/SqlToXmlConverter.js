// SqlToXmlConverter.js
import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import axios from 'axios';

function SqlToXmlConverter({ recordIdFields }) {  // Receive recordIdFields as prop
    const handleGenerateXml = async () => {
        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_URL}/generate_xml`,
                { record_id_fields: recordIdFields },
                { responseType: 'blob' }
            );

            const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/xml' }));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'generated_queries.xml');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error generating XML:", error);
        }
    };

    return (
        <Box textAlign="center">
            <Typography variant="h5">Generate Job File</Typography>
            <Button variant="contained" color="primary" onClick={handleGenerateXml}>
                Download
            </Button>
        </Box>
    );
}

export default SqlToXmlConverter;
