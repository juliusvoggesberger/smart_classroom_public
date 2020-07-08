import {PresentationCommunicator} from "./PresentationCommunicator";

/**
 * A class that creates and updates a plan for the school subjects of one week
 */
export class Plan {

    subjects: Array<Array<any>> = [[], [], [], [], []]; // One subject list for each day (0-Monday .. 4-Friday)
    daySelected: number;

    constructor() {
    }

    /**
     * Initialize the substitution plan with the most recent data from the database
     */
    init(): Promise<boolean> {
        // Start with Monday as the standard date
        this.daySelected = 0;

        let self = this;

        // Initialize the plan, by grabbing the data from influxdb
        const Influx = require('influx');
        const influx = new Influx.InfluxDB('http://db:pw@hostname:1234/db');
        let promise: Promise<boolean> = new Promise<boolean>(function (resolve) {
            influx.query('SELECT * FROM "subject data"')
                .then(result => {
                    self.createInitialPlan(result)
                })
                .catch(error => console.log(error));
        });
        PresentationCommunicator.getInstance().plan = this;
        return promise
    };


    /**
     * Reloads the plan template to show changes
     * @param day: the current selected day which is shown on the website
     */
    reloadTemplate(day: number): Promise<string> {

        let template = require('./templates/substitutionPlan.hbs');
        let rendered = template(
            {
                data: this.subjects[day]
            });

        return Promise.resolve(rendered)
    }

    /**
     * Adds a subject to the substitution plan
     * @param subj the subject to be added
     * @param day the day the subject will be held
     * @param ts the timestamp the subject was added. Allows to compare for newer changes
     */
    addSubject(subj: Subject, day: number, ts): void {
        this.subjects[subj.day].push({
            name: subj.name,
            slot: subj.slot,
            time: this.slotToTime(subj.slot),
            teacher: subj.teacher,
            status: this.setStatus(subj.status),
            ts: ts,
            color: this.setColor(subj.status)
        });
    }

    /**
     * Updates a subject given a mqtt message, or adds it if it does not exist yet.
     * This is needed for adding a replacement teacher for a subject with an ill teacher.
     * @param data the mqtt message of the form {"subject": subject, "teacher": teacher, "slot": slot}
     */
    changeSubject(data: any): void {
        let subj = data["subject"];
        let teach = data["teacher"];
        let ds = this.getDayAndSlot(data["slot"]);
        let day = ds[0];
        let slot = ds[1];
        let ts = data["time"];
        let changed = false;
        // Search for the subject that has to be updated
        if (teach !== "") {
            for (let i = 0; i < this.subjects[day].length; i++) {
                if (this.subjects[day][i]["name"] == subj && this.subjects[day][i]["slot"] == slot) {
                    // If the subject already exist, update it
                    let status = 'Regular';
                    let color = '#ffffff';
                    if (this.subjects[day][i]["teacher"] == "") {
                        status = 'Substitution';
                        color = '#e8bf43';
                    }
                    this.subjects[day][i]["teacher"] = teach;
                    this.subjects[day][i]["status"] = status;
                    this.subjects[day][i]["color"] = color;
                    changed = true;
                    break;
                }
            }
        }
        if (!changed) {
            // If the subject does not exist, create it
            let status = 0;
            if (teach == "") {
                status = 2;
            }
            if (!this.checkForDuplicate(slot, subj, teach, day, ts)) {
                let sub = new Subject(subj, slot, day, teach, status);
                if (teach == "") {
                    sub.cancelSubject()
                }
                this.addSubject(sub, day, ts);
            }
        }
        // Lastly reload the template
        this.reloadTemplate(this.daySelected).then(function (template) {
            document.getElementById("subsPlan").innerHTML = template;
        })
    }

    /**
     * Initial creation of the substitution plan
     * @param data the data from the db
     */
    createInitialPlan(data: Array<Object>): void {
        let sub: Subject;
        for (let i = 0; i < data.length; i++) {
            let status = 0;
            let ds = this.getDayAndSlot(data[i]["slot"]);
            let day = ds[0];
            let slot = ds[1];
            let ts = data[i]["time"];
            // As it is possible that there are multiple entries for the same subject, only take the newest one
            if (!this.checkForDuplicate(slot, data[i]["subject"], data[i]["teacher"], day, ts)) {
                sub = new Subject(data[i]["subject"], slot, day, data[i]["teacher"], status);
                if (data[i]["teacher"] == "") {
                    sub.cancelSubject()
                }
                this.addSubject(sub, day, ts);
            }
        }
        // Sort the list of the current day after the time slots
        for (let s of this.subjects) {
            s.sort(this.compare)
        }

        // Reload the substitution plan, so that the plan is shown
        this.reloadTemplate(this.daySelected).then(function (template) {
            document.getElementById("subsPlan").innerHTML = template;
        })
    }

    /**
     * A subject has a slot between 1 and 25.
     * There are 5 slots per day, so these have to be reformatted to the days 0(monday)-4(friday) and 1-5 per day
     * @param val the original slot value
     * @return A list with two values [day, slot]
     */
    getDayAndSlot(val: number): Array<number> {
        let day: number;
        let slot: number;
        if (val < 6) {
            day = 0;
            slot = val
        } else if (val < 11 && val > 5) {
            day = 1;
            slot = val - 5
        } else if (val < 16 && val > 10) {
            day = 2;
            slot = val - 10
        } else if (val < 21 && val > 15) {
            day = 3;
            slot = val - 15
        } else if (val > 20) {
            day = 4;
            slot = val - 20
        }
        return [day, slot]
    }

    /**
     * Checks if a subject already exists in the substitution plan.
     * If it does, check which one is newer and act accordingly.
     * @param slot The slot of the subject we want to check.
     * @param name The name of the subject we want to check.
     * @param teacher The teacher of the subject we want to check.
     * @param day The day of the subject we want to check.
     * @param ts The timestamp of the subject we want to check.
     */
    checkForDuplicate(slot, name, teacher, day, ts): boolean {
        for (let i = 0; i < this.subjects[day].length; i++) {
            if (this.subjects[day][i]["slot"] === slot && this.subjects[day][i]["name"] === name) {
                if (ts > this.subjects[day][i]["ts"]) {
                    this.subjects[day][i]["teacher"] = teacher;
                    if (teacher != "") {
                        this.subjects[day][i]["status"] = "Regular";
                        this.subjects[day][i]["color"] = '#ffffff';
                    } else {
                        this.subjects[day][i]["status"] = "Sick";
                        this.subjects[day][i]["color"] = '#f49089';
                    }
                }
                return true;
            }
        }
    }

    setStatus(status: number): string {
        switch (status) {
            case 0:
                return "Regular";
            case 1:
                return "Substitution";
            case 2:
                return "Sick";

        }
    }

    setColor(status: number) {
        switch (status) {
            case 0:
                return '#ffffff';
            case 1:
                return '#e8bf43';
            case 2:
                return '#f49089';

        }
    }

    slotToTime(slot: number): string {
        console.log(slot);
        switch (+slot) {
            case 1:
                return "8:00";
            case 2:
                return "9:45";
            case 3:
                return "11:30";
            case 4:
                return "14:00";
            case 5:
                return "15:45";
        }
    }

    compare(o1, o2): number {
        if (o1.slot < o2.slot) {
            return -1;
        }
        if (o1.slot > o2.slot) {
            return 1;
        }
        return 0;
    }
}

/**
 * Holds the information about a subject
 */
class Subject {

    name: string;
    slot: number;
    day: number;
    teacher: string;
    status: number;


    /**
     * Constructor of a subject
     * @param name the name of the subject
     * @param slot the slot the subject will take place in. Number between 1 and 5
     * @param day the day the subject will take place in. Number between 0(Monday) and 4(Friday)
     * @param teacher the teacher which will teach the subject on that day
     * @param status the status of the teacher: 0(Regular), 1(Substitution), 2(Ill)
     */
    constructor(name: string, slot: number, day: number, teacher: string, status: number) {
        this.name = name;
        this.slot = slot;
        this.day = day;
        this.teacher = teacher;
        // status: 0 = regular, 1 = substitution, 2 = canceled
        this.status = status;
    }

    setSubstitutionTeacher(teacher: string) {
        this.teacher = teacher;
        this.status = 1;
    }

    cancelSubject() {
        this.status = 2
    }
}
