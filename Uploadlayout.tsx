import React, { useState } from "react";
import {
  Button,
  Input,
  Text,
  Dialog,
  DataTable,
  Toaster,
  Tooltip,
  Checkbox
} from "your-ui-library"; // Replace with your actual UI library imports

const FileUploadPage = () => {
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadFiles, setUploadFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDelete, setIsDelete] = useState(false);

  const handleFileUpload = (files) => {
    // Handle file upload logic here
    setUploadFiles(files);
  };

  const handleDelete = () => {
    // Handle delete logic here
    setIsDelete(false);
  };

  return (
    <div className="w-full flex flex-col gap-4 p-4 h-full overflow-hidden">
      
      {/* Upload File Section */}
      <div className="flex flex-col bg-gray-100 rounded-lg p-4 border border-gray-300">
        <div className="flex justify-between items-center">
          <Text variant="large">Upload Files</Text>
          <Button variant="primary" onClick={() => setShowUploadDialog(true)}>
            Upload
          </Button>
        </div>
        
        <div
          className="flex flex-col items-center gap-2 mt-4 p-4 border border-dashed border-gray-400 rounded-lg cursor-pointer"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            handleFileUpload(Array.from(e.dataTransfer.files));
          }}
        >
          <Text variant="muted">Drag and Drop your files here or click to upload</Text>
          <Text variant="default">Supported formats include .pdf, .txt, .json</Text>
          <input
            type="file"
            accept=".pdf,.txt,.doc,.docx,.csv,.json"
            multiple
            className="hidden"
            onChange={(e) => handleFileUpload(Array.from(e.target.files))}
          />
        </div>
      </div>

      {/* Uploaded Files Data Table */}
      <div className="flex flex-col bg-white rounded-lg p-4 border border-gray-300 overflow-hidden">
        <Text variant="large" className="mb-4">Uploaded Files</Text>
        <div className="overflow-y-auto max-h-64">
          <DataTable
            columns={[
              { name: "File Name", selector: (row) => row.fileName },
              { name: "Status", selector: (row) => row.status }
            ]}
            data={uploadFiles}
            selectableRows
            onSelectedRowsChange={(selected) => setSelectedFiles(selected)}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-2 mt-4">
        <Button variant="secondary" onClick={() => setShowUploadDialog(false)}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={() => {
            // Add action for processing files
          }}
          disabled={uploadFiles.length === 0}
        >
          Proceed
        </Button>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDelete} onClose={() => setIsDelete(false)}>
        <Dialog.Content>
          <Dialog.Header>
            <Dialog.Title>Delete Document</Dialog.Title>
          </Dialog.Header>
          <Dialog.Description>
            Are you sure you want to delete the document permanently?
          </Dialog.Description>
          <Dialog.Footer>
            <Button onClick={() => setIsDelete(false)} variant="secondary">
              No
            </Button>
            <Button onClick={handleDelete} variant="primary">
              Yes
            </Button>
          </Dialog.Footer>
        </Dialog.Content>
      </Dialog>

      {/* Upload Dialog */}
      <Dialog open={showUploadDialog} onClose={() => setShowUploadDialog(false)}>
        <Dialog.Content>
          <Dialog.Header>
            <Dialog.Title>Upload Documents</Dialog.Title>
          </Dialog.Header>
          <Dialog.Description>
            Please select files to upload. Only .pdf, .txt, and .json formats are allowed.
          </Dialog.Description>
          <div className="flex flex-col gap-4 mt-4">
            {uploadFiles.map((file, index) => (
              <div key={index} className="flex items-center gap-4">
                <Checkbox checked={file.checked} onChange={() => {}} />
                <Text>{file.fileName}</Text>
                {file.duplicate && (
                  <Tooltip content="This file already exists. Uploading again will overwrite existing data">
                    <Text variant="warning">Duplicate</Text>
                  </Tooltip>
                )}
              </div>
            ))}
          </div>
          <Dialog.Footer>
            <Button variant="secondary" onClick={() => setShowUploadDialog(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={() => {}}>
              Proceed
            </Button>
          </Dialog.Footer>
        </Dialog.Content>
      </Dialog>

      {/* Toaster for Notifications */}
      <Toaster />
    </div>
  );
};

export default FileUploadPage;
