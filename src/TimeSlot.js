import React from "react";

const TimeSlot = (time_obj, onCheck) => {
    return (<li className="timeSlotObject">
        <input
            type='checkbox'
            className={`checkbox-${time_obj['status']}`}
            id={time_obj['id']}
            value={time_obj['id']}
            key={time_obj['id']}
            onChange={(e) => onCheck(e)}
            disabled={['BOOKED', 'FULL', 'UNKNOWN', 'WAITINGLIST'].includes(time_obj['status'])}
        />
        <label htmlFor={time_obj['id']}>{time_obj['start']}-{time_obj['end']}</label>
    </li>)
}

export default TimeSlot