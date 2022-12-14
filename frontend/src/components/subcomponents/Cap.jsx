import { Link, useNavigate } from "react-router-dom";
import { useState } from 'react';

import "../../css/sign.css"

const Cap = (props) => {
    const [findValue, setFindValue] = useState("")
    let navigate = useNavigate()
    
    function find() {
        if (findValue.length === 0) {

        } else {
            setFindValue("")
            window.location.href = `/find/${findValue}`
            navigate(`/find/${findValue}`)
        }
    }
    return (
        <>
            <div className="cap__wrapper">
                <div className="cap">
                    <div className="container-4">
                        <input type="search" id="search" placeholder="Поиск..." onChange={e => setFindValue(e.target.value)} value={findValue} />
                        <button className="icon" style={{marginBottom: "2.5px"}} onClick={find}><i className="fa fa-search"></i></button>
                        <Link to="/enroll"><button style={{marginLeft: "3vh", height: "50px"}} className="beautifulButton">Запись к врачу</button></Link>
                    </div>
                </div>


                {props.flag ?  
                <div className="nav">
                    <nav>
                        <ul>
                            <li style={{textTransform: "capitalize"}}><Link to="/information">{props.user.username}</Link></li>
                            <li><ion-icon name="notifications-outline" style={{fontSize: "30px", color: "#34D178", cursor: "pointer"}}></ion-icon></li>
                            <li><ion-icon name="bookmark-outline" style={{fontSize: "30px", color: "#34D178", cursor: "pointer"}}></ion-icon></li>
                            <li>
                                <div className="nav__img">
                                    <img src={props.user.photo} alt="" />
                                    {console.log(props.user)}
                                </div>
                            </li>
                        </ul>
                    </nav>
                </div>
                :
                <div className="nav">
                    <nav>
                        <ul>
                            <li><Link to="/signup">Регистрация</Link></li>
                            <li><Link to="/signin">Авторизация</Link></li>
                            <li><ion-icon name="notifications-outline" style={{fontSize: "30px", color: "#34D178", cursor: "pointer"}}></ion-icon></li>
                            <li><ion-icon name="bookmark-outline" style={{fontSize: "30px", color: "#34D178", cursor: "pointer"}}></ion-icon></li>
                            <li>
                                <div className="nav__img">
                                    <img src="https://www.meme-arsenal.com/memes/723c78e9be76eba2598c2d4c611f994c.jpg" alt="" />
                                </div>
                            </li>
                        </ul>
                    </nav>
                </div>}
            </div>




            

        </>
    );
};

export default Cap;