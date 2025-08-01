import React from 'react';

const ErrorDisplay = ({ error, className = '' }) => {
  if (!error) return null;
  const renderErrors = () => {
    if (error.details) {
      const { details } = error;
      const errors = [];

      if (details.non_field_errors && Array.isArray(details.non_field_errors)) {
        details.non_field_errors.forEach((msg, index) => {
          errors.push(
            <div key={`non_field_${index}`} className="alert alert-danger mb-2">
              {msg}
            </div>
          );
        });
      }

      Object.keys(details).forEach(field => {
        if (field !== 'non_field_errors' && Array.isArray(details[field])) {
          details[field].forEach((msg, index) => {
            errors.push(
              <div key={`${field}_${index}`} className="alert alert-danger mb-2">
                <strong>{field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {msg}
              </div>
            );
          });
        } else if (field !== 'non_field_errors' && typeof details[field] === 'string') {
          errors.push(
            <div key={field} className="alert alert-danger mb-2">
              <strong>{field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {details[field]}
            </div>
          );
        }
      });

      return errors.length > 0 ? errors : (
        <div className="alert alert-danger mb-2">
          An error occurred. Please try again.
        </div>
      );
    }

    if (typeof error === 'string') {
      return (
        <div className="alert alert-danger mb-2">
          {error}
        </div>
      );
    }

    if (error.message) {
      return (
        <div className="alert alert-danger mb-2">
          {error.message}
        </div>
      );
    }

    return (
      <div className="alert alert-danger mb-2">
        An unexpected error occurred. Please try again.
      </div>
    );
  };

  return (
    <div className={className}>
      {renderErrors()}
    </div>
  );
};

export default ErrorDisplay;