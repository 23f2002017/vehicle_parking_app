export default {
    template : `
        <div style="padding-bottom: 20px;">
            <h2>Parking Lot Details</h2>
            <div >
                <div style="padding: 0px 10px;">
                    <span style="font-size: xx-large;">{{LotDetails.name}}</span>
                    <span style="padding-left: 15px; font-size: large;">{{LotDetails.address}}, <b>{{LotDetails.pincode}}</b></span>
                </div>
                <div style="padding: 10px; font-size: large;">
                    <span><b>Lot ID</b> : {{LotDetails.id}}</span>
                    <span style="padding-left: 50px;"><b>Total Spots</b> : {{LotDetails.no_of_spots}}</span>
                    <span style="padding-left: 50px;"><b>Spots Available</b> : {{LotDetails.no_of_spots_available}}</span>   
                </div>
                <div style="padding: 10px; font-size: large;">
                    <span><b>Total Vehicles Ever Parked</b> : {{LotDetails.total_vehicles_ever_parked}}</span>
                </div>
                <div style="padding: 10px;">
                    <span style="font-size: large;"><b>Price</b> : </span>
                    <span style="font-size: xx-large;">Rs. {{LotDetails.price}}/hr</span>
                </div>
            </div>
            <hr/> 
            <h2>Parking Spots</h2> 
            <div>
                <div v-for="spot in spots" style="padding: 5px; margin-right: 300px; font-size: medium">
                    <div style="border: 1px solid black; border-radius: 5px; padding: 8px; background-color: #f3f2f2ff;">
                        <details @click="() => GetSpotDetails(spot.id)">
                            <summary>
                                <span style="padding-left: 20px;"><b>Spot ID</b> : {{spot.id}}</span>
                                <span style="padding-left: 50px;"><b>Spot no.</b> : {{spot.spot_no}}</span>
                                <span style="padding-left: 50px;"><b>Status</b> : {{spot.status}}</span>  
                                <button v-if="spot.status == 'available'" @click="() => DeleteSpot(spot.id)" style="float: right;"> Delete Spot </button>
                                <button v-else style="float: right;" disabled> Delete Spot </button> 
                            </summary> 
                            <div v-if="ClickedSpot === spot.id" style="padding-left: 20px; font-size: medium;">
                                <hr/> 
                                <div v-if="spot.status == 'occupied'">
                                    <h3>Current Parking Details </h3>
                                    <p style="padding-left: 30px;"><b>Parking ID</b> : {{SpotDetails.current_parking.parking_id}}</p> 
                                    <p style="padding-left: 30px;"><b>Customer ID</b> : {{SpotDetails.current_parking.customer_id}}</p>
                                    <p style="padding-left: 30px;"><b>Vehicle Reg no.</b> : {{SpotDetails.current_parking.vehicle_reg_no}}</p>
                                    <p style="padding-left: 30px;"><b>Parking Time</b> : {{SpotDetails.current_parking.parking_time}}</p>
                                </div>     
                                <p><b>Total parkings made on this spot</b> : {{SpotDetails.total_vehicles_ever_parked}}</p>  
                            </div>    
                        </details>    
                    </div>
                </div>
            </div>  
        </div>
    `,
    data() {
        return {
            LotDetails : {},
            spots : [],
            message : "",
            SpotDetails : {},
            ClickedSpot: null
        }
    },
    methods : {
        GetLot : async function() {
            const res = await fetch(`/api/parking_lot/${this.$route.params.id}`, {
            method : "GET",
            headers : {
                "Content-Type" : "application/json",
                "auth-token" : localStorage.getItem("auth_token")
            } 
            })
            const data = await res.json()
            if (res.ok) {
                this.LotDetails = data.parking_lot_details
                this.spots = data.parking_spots
            } else {
                this.message = data.message
            }
        },
        GetSpotDetails: async function(id) {
            this.ClickedSpot = id
            const res = await fetch(`/api/parking_spot/${id}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "auth-token": localStorage.getItem("auth_token")
                }
            })
            const data = await res.json()
            if (res.ok) {
                this.SpotDetails = data
                console.log(this.SpotDetails)
            }    
        },
        DeleteSpot : async function(spot_id) {
            fetch(`/api/parking_spot/${spot_id}`, {
                method: "DELETE",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token")
                }
            }).then(res => res.json()).then(data => {
                alert(data.message)
                this.GetLot()
            })
        }
    },
    mounted() {
        this.GetLot()
    }
}