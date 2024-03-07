import React from 'react';

class UnsafeComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      userInput: ''
    };
  }

  handleChange = (event) => {
    this.setState({ userInput: event.target.value });
  };

  render() {
    return (
      <div>
        <h2>Unsafe Component</h2>
        <input type="text" onChange={this.handleChange} placeholder="Type something..." />
        <div dangerouslySetInnerHTML={{ __html: this.state.userInput }}></div>
      </div>
    );
  }
}

export default UnsafeComponent;
