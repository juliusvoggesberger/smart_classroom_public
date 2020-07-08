import {Plan} from './plan'

/**
 *
 */
export class PresentationCommunicator {
    private static instance: PresentationCommunicator;

    mqtt = require('mqtt');
    client: any;
    plan: Plan;
    frontend: any;

    constructor() {
    }

    /**
     * Checks if an instance of this class already exists.
     * If not create one.
     */
    static getInstance() {
        if (!PresentationCommunicator.instance) {
            PresentationCommunicator.instance = new PresentationCommunicator();
        }
        return PresentationCommunicator.instance;
    }

    setFrontend(frontend) {
        this.frontend = frontend
    }


    /**
     * Checks for mqtt messages
     */
    init(): Promise<any> {
        let self = this;

        let promise: Promise<boolean> = new Promise<boolean>(function (resolve) {
            // First connect to the client
            self.client = self.mqtt.connect('mqtt://hostname:1234', {
                "username": "user",
                "password": "pw"
            });

            //register mqtt
            self.client.on('connect', function () {
                self.client.subscribe('smart_classroom/backend/#');
                console.log("connected to MQTT-Broker");
                resolve(true)
            });

            // Receive mqtt messages
            self.client.on('message', function (topic, message) {
                console.log("Message received");
                message = JSON.parse(message);
                switch (topic) {
                    case "smart_classroom/backend/sensordata":
                        self.setSensorValues(message);
                        break;
                    case "smart_classroom/backend/lesson":
                        if (self.plan != undefined) {
                            // Add changes to the substitution plan
                            self.plan.changeSubject(message);
                        }
                        break;
                    default:
                        console.info("Unknown topic!")
                }

            });
        });

        return promise
    }

    /**
     * Given a mqtt message change the sensor values in the web page
     * @param msg The data which is published to the backend. It can have two forms:
     Either the list will have a length of 2: [timestamp, sensor data]
     Or it will have a length of 4: [timestamp, sensor data, subject data, teacher data]
     */
    setSensorValues(msg: any): void {

        // Get the sensor values and add the according unit
        let tempIn = this.round2dec(msg[1]['temp_in']) + " °C";
        let tempOut = this.round2dec(msg[1]['temp_out']) + " °C";
        let lightIn = this.round2dec(msg[1]['light_in']) + " Lux";
        let lightOut = this.round2dec(msg[1]['light_out']) + " Lux";
        let blight = this.round2dec(msg[1]["light_board"]) + "Lux";
        let humIn = this.round2dec(msg[1]['humidity_in']) + " %";
        let humOut = this.round2dec(msg[1]['humidity_out']) + " %";

        // Set the data in the front end
        document.getElementById("tempIn").innerText = tempIn;
        document.getElementById("tempOut").innerText = tempOut;
        document.getElementById("lightIn").innerText = lightIn;
        document.getElementById("lightOut").innerText = lightOut;
        document.getElementById("boardlight").innerText = blight;
        document.getElementById("humidityIn").innerText = humIn;
        document.getElementById("humidityOut").innerText = humOut;

        // Additionally set the time
        let date = new Date(msg[0] * 1000);
        document.getElementById("time").innerText = this.formatTime(date)

    }

    formatTime(date: Date): string {
        let hours = date.getHours();
        let minutes = "0" + date.getMinutes();
        let formattedTime = hours + ':' + minutes.substr(-2);
        let day = date.getDay();
        let month = date.getMonth() + 1;
        let year = date.getFullYear();
        let formattedDate = day + "." + month + "." + year;
        return formattedDate + " " + formattedTime
    }

    /**
     * A simple methods that rounds an input to two decimals
     * @param val the input to be rounded
     * @return the input rounded to two decimals
     */
    round2dec(val: number): number {
        return Math.round(val * 100) / 100;
    }
}
