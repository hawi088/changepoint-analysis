import React, { useState } from 'react';

const FilterControls = ({ onApply, startDate: initialStart, endDate: initialEnd }) => {
  const [startDate, setStartDate] = useState(initialStart || '1987-05-20');
  const [endDate, setEndDate] = useState(initialEnd || '2022-11-14');

  const handleSubmit = (e) => {
    e.preventDefault();
    onApply(startDate, endDate);
  };

  return (
    <form className="filter-controls" onSubmit={handleSubmit}>
      <label>
        Start Date
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
      </label>
      <label>
        End Date
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />
      </label>
      <button type="submit">Apply Filter</button>
    </form>
  );
};

export default FilterControls;