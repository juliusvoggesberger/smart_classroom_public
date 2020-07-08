import {Plan} from './plan'
import {PresentationCommunicator} from "./PresentationCommunicator";

export class FrontendHandler {

    plan: any;

    constructor() {
    }

    /**
     * Load the substitution plan and checks for event messages
     */
    init(): Promise<boolean> {

        // Initialize the substitution plan
        this.plan = new Plan();
        this.plan.init();

        let self = this;
        let promise: Promise<boolean> = new Promise<boolean>(function (resolve) {

            // Teacher/Student toggle
            document.getElementById("teacherButton").addEventListener('click', function (e) {
                document.getElementById("sensActControl").hidden = false;
                document.getElementById("teacherButton").className = 'btn btn-primary active';
                document.getElementById("studentButton").className = 'btn btn-secondary';
                document.forms["toggleForm"].elements["student"].checked = false;
                document.forms["toggleForm"].elements["teacher"].checked = true;
                console.log('TEACHER')
            });

            document.getElementById("studentButton").addEventListener('click', function (e) {
                document.getElementById("sensActControl").hidden = true;
                document.getElementById("teacherButton").className = 'btn btn-secondary';
                document.getElementById("studentButton").className = 'btn btn-primary active';
                document.forms["toggleForm"].elements["student"].checked = true;
                document.forms["toggleForm"].elements["teacher"].checked = false;
                console.log('Student')
            });

            // Window Dropdown
            document.getElementById("windowDropdown").addEventListener('change', function (e) {
                console.log("Window");
                let value = document.forms["actuatorsForm"].elements["windowDropdown"].value;
                self.publishActuatorStatus('window', +value);
            });

            // Humidity Dropdown
            document.getElementById("humidityDropdown").addEventListener('change', function (e) {
                console.log("Humidity");
                let value = document.forms["actuatorsForm"].elements["humidityDropdown"].value;
                self.publishActuatorStatus('humidifier', +value);
            });

            // AC Dropdown
            document.getElementById("acDropdown").addEventListener('change', function (e) {
                console.log("AC");
                let value = document.forms["actuatorsForm"].elements["acDropdown"].value;
                self.publishActuatorStatus('ac', +value);
            });

            // Shutter Input
            document.getElementById("shutterStat").addEventListener('change', function (e) {
                console.log("Shutter");
                let value = document.forms["actuatorsForm"].elements["shutterStat"].value;
                if (self.checkForCorrectRange('shutter', +value)) {
                    document.getElementById("shutterWarning").hidden = true;
                    self.publishActuatorStatus('shutters', +value);
                }
            });

            // Light Input
            document.getElementById("lightInput").addEventListener('change', function (e) {
                console.log("Light");
                let value = document.forms["actuatorsForm"].elements["lightInput"].value;
                if (self.checkForCorrectRange('light', value)) {
                    document.getElementById("lightWarning").hidden = true;
                    self.publishActuatorStatus('light', +value);
                }

            });

            // Temperature Input
            document.getElementById("tempInput").addEventListener('change', function (e) {
                console.log("Temperature");
                let value = document.forms["actuatorsForm"].elements["tempInput"].value;
                self.publishActuatorStatus('radiators', +value);
            });

            // Load substitution plan
            self.loadTemplate().then(function (template) {
                document.getElementById("subsPlan").innerHTML = template;
                resolve(true)
            });

            // Reload plan for chosen day
            document.getElementById("dayDiv").addEventListener('click', function (e) {
                let form = document.forms["dayForm"];
                let id = (<HTMLElement>e.target).id;
                id = document.getElementById(id).children[0].id;
                self.plan.daySelected = form.elements[id].value;
                self.plan.reloadTemplate(form.elements[id].value).then(function (template) {
                    document.getElementById("subsPlan").innerHTML = template;
                    resolve(true)
                })
            });
        });

        return promise
    }

    /**
     * Loads the substitution plan template
     */
    loadTemplate(): Promise<string> {
        let template = require('./templates/substitutionPlan.hbs');
        let rendered = template(
            {
                data: this.plan.subjects[0]
            });
        return Promise.resolve(rendered)
    }

    /**
     * Publish changes to the actuators to the physical layer
     * @param actuator the actuator which status will be changed
     * @param status the status which will be set
     */
    publishActuatorStatus(actuator: string, status: number) {
        console.log("PUBLISHING");
        PresentationCommunicator.getInstance().client.publish("smart_classroom/physical/manual", JSON.stringify({
            "actuator": actuator,
            "status": status
        }));
    }

    /**
     * Check if an input for an actuator is in the correct interval
     * @param topic the actuator which will be checked
     * @param value the status which is set
     */
    checkForCorrectRange(topic: string, value: number): boolean {

        let accepted = true;

        switch (topic) {

            case 'shutter':
                if (value < 0 || value > 100) {
                    document.getElementById("shutterWarning").hidden = false;
                    accepted = false;
                }
                break;
            case 'light':
                if (value < 0 || value > 500) {
                    document.getElementById("lightWarning").hidden = false;
                    accepted = false;
                }
                break;
            default:
                console.log("Unknown topic")
        }

        return accepted
    }

}
