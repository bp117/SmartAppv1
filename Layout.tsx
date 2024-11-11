<div className="left-section">
  {isFileSummaryVisible ? (
    // File Summary section displayed as an inline "sheet"
    <div className="file-summary-sheet">
      <div className="file-summary-header">
        <h3>File Summary</h3>
        <button onClick={toggleFileSummary}>Close</button>
      </div>
      <div className="file-summary-content">
        {/* Add your existing file summary content here */}
        {/* For example, key topics, summary details */}
      </div>
    </div>
  ) : (
    // Uploaded Documents section, hidden when File Summary is open
    <div className="uploaded-documents">
      <button onClick={toggleFileSummary}>View File Summary</button>
      {/* Existing uploaded documents code here */}
    </div>
  )}
</div>

.left-section {
  width: 30%; /* Adjust width as needed */
  transition: width 0.3s ease;
}

.file-summary-sheet {
  border: 1px solid #e0e0e0; /* Light border for sheet appearance */
  border-radius: 8px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* Soft shadow for sheet look */
  padding: 16px;
  background-color: #ffffff; /* White background to resemble sheet */
}

.file-summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 8px;
  margin-bottom: 16px;
}

.file-summary-content {
  max-height: 400px; /* Adjust height as needed */
  overflow-y: auto;
}

<div className={`right-section ${isFileSummaryVisible ? 'expanded-layout' : ''}`}>
  {/* Right section content */}
</div>

<div className="file-summary-content">
  <h4>Key Topics</h4>
  <ul>
    {keyTopics.map((topic, index) => (
      <li key={index} onClick={() => handleKeyTopicClick(topic)}>
        {topic}
      </li>
    ))}
  </ul>
</div>

const handleKeyTopicClick = (topic) => {
  // Logic to send the topic as a message
};

import React, { useState } from 'react';
import { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@radix-ui/react-sheet';
import { Button } from '@radix-ui/react-button';

const DocumentManager = () => {
  const [isFileSummaryVisible, setFileSummaryVisible] = useState(false);
  const [keyTopics, setKeyTopics] = useState(['Topic 1', 'Topic 2', 'Topic 3']); // Sample topics

  // Function to toggle between Uploaded Documents and File Summary
  const toggleFileSummary = () => {
    setFileSummaryVisible(!isFileSummaryVisible);
  };

  const handleKeyTopicClick = (topic) => {
    // Logic to send the topic as a message
    console.log(`Sending message with topic: ${topic}`);
  };

  return (
    <div className="flex">
      {/* Left Section */}
      <div className="left-section w-1/3 p-4">
        {isFileSummaryVisible ? (
          // File Summary section displayed as an inline "sheet"
          <div className="file-summary-sheet border rounded-lg shadow p-4 bg-white">
            <div className="file-summary-header flex justify-between items-center border-b pb-2 mb-4">
              <h3 className="text-lg font-semibold">File Summary</h3>
              <Button onClick={toggleFileSummary} variant="ghost" size="small">Close</Button>
            </div>
            <div className="file-summary-content max-h-96 overflow-y-auto">
              <SheetHeader>
                <SheetTitle>Key Topics</SheetTitle>
                <SheetDescription>Select a topic to trigger a message</SheetDescription>
              </SheetHeader>
              <ul>
                {keyTopics.map((topic, index) => (
                  <li
                    key={index}
                    onClick={() => handleKeyTopicClick(topic)}
                    className="cursor-pointer p-2 hover:bg-gray-100 rounded"
                  >
                    {topic}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          // Uploaded Documents section, hidden when File Summary is open
          <div className="uploaded-documents">
            <Button onClick={toggleFileSummary} variant="secondary">View File Summary</Button>
            {/* Existing uploaded documents content goes here */}
            <p className="mt-4">Uploaded Documents will appear here when File Summary is closed.</p>
          </div>
        )}
      </div>

      {/* Right Section */}
      <div className={`right-section ${isFileSummaryVisible ? 'w-2/3' : 'w-3/4'} p-4 transition-all`}>
        {/* Right section content */}
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="secondary">System Instructions</Button>
          </SheetTrigger>
          <SheetContent side="right" className="bg-white p-6 shadow-md rounded-lg">
            <SheetHeader>
              <SheetTitle>System Instructions</SheetTitle>
              <SheetDescription>
                You can provide additional instructions here.
              </SheetDescription>
            </SheetHeader>
            {/* System Instructions Text Area */}
            <textarea
              name="systemMessage"
              className="w-full h-32 border rounded p-2 mt-4"
              placeholder="Enter additional instructions here"
            />
          </SheetContent>
        </Sheet>

        {/* Placeholder for more content in the right section */}
        <div className="mt-6">
          <p className="text-gray-500">Additional right-side content goes here.</p>
        </div>
      </div>
    </div>
  );
};

export default DocumentManager;
