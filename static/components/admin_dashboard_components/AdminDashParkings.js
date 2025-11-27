export default {
    template : `
        <div style="padding-bottom: 20px;">
            <p v-if='message != ""' style="color: red">{{message}}</p>
            <div v-else>
                <h2>Parkings</h2>
                <div style="border: 3px solid black; width: 1000px;">
                    <div v-for="parking in parkings">
                        <div style="padding: 5px;">
                            <div style="border: 3px solid black;">
                                <div style="padding: 10px;">
                                    <span style="font-size: xx-large;">{{parking.vehicle_reg_no}}</span>
                                    <span style="padding-left: 25px; font-size: large;">Parking was made by {{parking.user_name}} at {{parking.lot_address}}</span>
                                    <span v-if="parking.exit_time" style="float: right; padding-right: 20px; font-size: xx-large;">Released</span>
                                    <span v-else style="float: right; padding-right: 20px; font-size: xx-large;">Occupied</span>
                                </div>
                                <div style="padding: 0px 0px 10px 10px;">
                                    <span style="font-size: large;"><b>Parking ID</b> : {{parking.id}}</span>
                                    <span style="padding-left: 50px; font-size: large;"><b>Lot ID</b> : {{parking.lot_id}}</span>
                                    <span style="padding-left: 50px; font-size: large;"><b>Spot No</b> : {{parking.spot_no}}</span>
                                    <span style="padding-left: 50px; font-size: large;"><b>User ID</b> : {{parking.user_id}}</span>
                                    <span style="padding-left: 50px; font-size: large;"><b>Parking Time</b> : {{parking.parking_time}}</span>
                                </div>
                                <div v-if="parking.exit_time" style="padding: 0px 0px 10px 10px;">
                                    <span style="font-size: large;"><b>Exit Time</b> : {{parking.exit_time}}</span>
                                    <span style="padding-left: 50px; font-size: large;"><b>Parking Charge</b> : Rs. {{parking.cost}}</span>
                                </div>
                            </div>
                        </div>
                    </div>   
                </div>    
            </div>    
        </div>    
    `,
    data() {
        return {
            message : "",
            parkings : []
        }
    },
    mounted : async function() {
        const res = await fetch("/api/parkings", {
            method: "GET",
            headers: {
                "auth-token" : localStorage.getItem("auth_token")
            }
        })
        const data = await res.json()
        if (res.ok) {
            this.parkings = data.parkings_list
        } else {
            this.message = data.message
        }
    }
}