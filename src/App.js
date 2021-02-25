import React, {useState, useEffect} from 'react';
import './App.css';
import Login from "./Login";
import Calender from "./Calender";

function App() {
    const [schedule, setSchedule] = useState(null);
    const [isLoading, setIsLoading] = useState(true)
    const [checked, setChecked] = useState([])
    const [user, setUser] = useState(null)

    const load_schedule = (isHardReset) => {
        setIsLoading(true)
        fetch(`/api/schedule?phone=${user.phone}&pwd=${user.pwd}`)
            .then(res => res.json())
            .then(data => {
                setSchedule(JSON.parse(data.schedule));
            })
            .then(_ => setIsLoading(false));
    }

    const logOut = () => {
        console.log('LOGG UT')
        setUser(null)
    }

    const onCalenderSubmit = async(e) => {
        e.preventDefault()
        const checkbox_ids = []

        for (const checkbox of checked) {
            checkbox.checked = false
            checkbox_ids.push(checkbox.value)
        }

        console.log(checkbox_ids)
        setIsLoading(true);

        fetch(`/api/book?phone=${user.phone}&pwd=${user.pwd}`, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, *cors, same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
              'Content-Type': 'application/json'
              // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            redirect: 'follow', // manual, *follow, error
            referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(checkbox_ids) // body data type must match "Content-Type" header
        })
            .then(res => res.json())
            .then(data => {
                console.log(data)
                setSchedule(data);
                setIsLoading(false);
        })
    }

    const onCheck = (e) => {
        if (e.target.checked) {
            setChecked(checked => [...checked, e.target]);
        } else {
            setChecked(checked.filter(item => item !== e.target));
        }
    }

    const onCredentialsSubmit = async(e) => {
        e.preventDefault();
        setUser({
            phone: e.target[0].value,
            pwd: e.target[1].value
        })
    }

    return (
        <div className="App">
            {!user && Login(onCredentialsSubmit)}
            {user && <Calender
                onSubmit={onCalenderSubmit}
                load={load_schedule}
                schedule={schedule}
                user={user}
                onCheck={onCheck}
                isLoading={isLoading}
                logOut={logOut}
            />
            }
        </div>
    );
}


const get_studio = studio_int => {
    const studios = {
        306: 'Gløshaugen',
        307: 'Dragvoll',
        308: 'Portalen',
        402: 'DMMH',
        540: 'Moholt'
    }

    return studios[studio_int]
}


export default App;