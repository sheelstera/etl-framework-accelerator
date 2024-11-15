// FileUpload.js
import React, { useState } from 'react';
import { Button, Box, Typography } from '@mui/material';
import { styled } from '@mui/system';
import axios from 'axios';

// Styled file input button
const StyledInput = styled('input')({
    display: 'none'
});

function FileUpload({ onUploadComplete }) {
    const [sqlFile, setSqlFile] = useState(null);
    const [yamlFile, setYamlFile] = useState(null);

    const handleSqlFileChange = (e) => setSqlFile(e.target.files[0]);
    const handleYamlFileChange = (e) => setYamlFile(e.target.files[0]);

    const handleUploadClick = async () => {
        const formData = new FormData();
        if (sqlFile) formData.append("sql_file", sqlFile);
        if (yamlFile) formData.append("yaml_file", yamlFile);

        try {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/upload_files`, formData);
            if (response.status === 200 && response.data.sourceAliases) {
                onUploadComplete(response.data.sourceAliases);
            } else {
                console.error("No source aliases received from the backend.");
            }
        } catch (error) {
            console.error("Error uploading files:", error);
        }
    };

    return (
        <Box textAlign="center">
            <Typography variant="h6">Step 1: Upload Config YAML and SQL Files</Typography>

            <Box mt={2}>
                <label htmlFor="sql-file">
                    <StyledInput id="sql-file" type="file" onChange={handleSqlFileChange} />
                    <Button variant="contained" component="span">
                        {sqlFile ? sqlFile.name : 'Choose SQL File'}
                    </Button>
                </label>
            </Box>

            <Box mt={2}>
                <label htmlFor="yaml-file">
                    <StyledInput id="yaml-file" type="file" onChange={handleYamlFileChange} />
                    <Button variant="contained" component="span">
                        {yamlFile ? yamlFile.name : 'Choose YAML Config File'}
                    </Button>
                </label>
            </Box>

            <Button
                variant="contained"
                color="primary"
                onClick={handleUploadClick}
                disabled={!sqlFile || !yamlFile}
                sx={{ mt: 2 }}
            >
                Upload Files
            </Button>
        </Box>
    );
}

export default FileUpload;
