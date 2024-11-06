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
    <div className="w-full flex flex-col gap-4 bg-card h-full overflow-hidden p-4">
  
  {/* Page Title */}
  <Text variant="h1">Build Your RAG Application</Text>

  {/* Upload Section */}
  <div className="flex flex-col bg-gray-100 rounded-lg p-4 border border-gray-300 mb-4">
    <div className="flex items-center gap-4">
      <CloudUpload strokeWidth={0.5} size={32} />
      <Text variant="large">Drag and Drop your files here or click to upload</Text>
    </div>
    <Text variant="default" className="mt-2">
      Supported formats include .pdf, .txt, .json (only for custom chunking strategy)
    </Text>
    <input
      type="file"
      accept=".pdf,.txt,.doc,.docx,.csv,.json"
      multiple
      className="hidden"
      onChange={(e) => handleFileUpload(Array.from(e.target.files as FileList))}
    />
  </div>

  {/* Uploaded Files Section */}
  <div className="flex flex-col flex-1 bg-white rounded-lg border border-gray-300 overflow-hidden">
    <Text variant="medium" className="px-4 pt-4 pb-2">Uploaded Files</Text>
    <div className="overflow-y-auto max-h-[50vh] px-4">
      <DataTable
        columns={uploadColumns}
        data={docManagementList}
        filterColumn="documentName"
        rowSelection={rowSelection}
        setRowSelection={setRowSelection}
        className="overflow-y-auto"
      />
    </div>
  </div>

  {/* Action Buttons */}
  <div className="flex justify-end items-center gap-4 mt-4">
    <Button variant="secondary" size="small" onClick={() => navigate("/myapps")}>
      Cancel
    </Button>
    <Button variant="default" size="small" onClick={checkValidDocs}>
      Continue
    </Button>
  </div>
</div>
</div>
  );
};

export default FileUploadPage;
