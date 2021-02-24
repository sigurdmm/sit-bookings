import React from 'react';
import {ReactComponent as ReloadLogo} from "./reload.svg";
import {ReactComponent as LogoutLogo} from "./logout.svg";
import LoadingIcon from "./LoadingIcon";
import TimeSlot from "./TimeSlot";


class Calender extends React.Component {

    componentDidMount() {
        this.props.load();
    }

    render_schedule() {
        return <>
            {Object.keys(this.props.schedule).map((date, date_key) => <div className="dateContainer">
                <ul>
                    <h3>{date}</h3>
                    {Object.keys(this.props.schedule[date]).map((day, day_key) => {
                        const day_obj = this.props.schedule[date][day]
                        return TimeSlot(day_obj, this.props.onCheck)
                    })
                    }
                </ul>
            </div>)
            }
        </>
    }


    render() {
        return <form id='scheduleForm' onSubmit={this.props.onSubmit}>
            <div id='headerContainer'>
                <button type='button' style={{height: '30px', width: "30px"}} onClick={() => this.props.logOut()}>
                    <LogoutLogo/>
                </button>
                <h1 id='formHeader'>Timebooking</h1>
                <button type='button' style={{height: '30px', width: "30px"}} onClick={() => this.props.load(true)}>
                    <ReloadLogo/>
                </button>
            </div>

            <div id="scheduleContainer">
                {this.props.isLoading && <LoadingIcon/>}
                {this.props.schedule && !this.props.isLoading && this.render_schedule(this.props.schedule, this.props.onCheck)}
            </div>
            <div id='footerContainer'>
                {this.props.schedule && this.props.user && !this.props.isLoading && <input id='formSubmit' type="submit" value="Book"/>}
                <p>© Sigurd Marius Melsom, 2021</p>
            </div>
        </form>
    }
}

export default Calender