class Dashboard {
	constructor(username, profile_id) {
		this.friendlist_api = '/user/friends'
		this.profile_api = '/profiles'
		this.friendsrequest_api = '/user/friendsrequest/'
		this.updatefriendrequest_api = '/user/friendsrequest/'
		this.message_api = '/user/messages?thread_id='
		this.send_message_api = '/user/message/send/'
		this.friendlistContainer = $('#friends-list')
		this.profilelistContainer = $('#profile-list')
		this.chatContainer = $('#chatcontainer')
		this.username = username
		this.profile_id = profile_id
	}

	init() {
		this.initfriends()
		this.initprofile()
		this.initSockets()
	}

	initSockets() {
		Dashboard.receiveFriendSocket(this.profile_id)
		Dashboard.openFriendSocket(this.profile_id)
		Dashboard.updateFriendsDetails(this.profile_id)
	}

	initprofile() {
		this.profile_api
		setTimeout(()=> {
			var response = Dashboard.send_xml_request('GET', this.profile_api)[0]
			var res = '<div class="row">'
			for (var i = response.length - 1; i >= 0; i--) {
				if (response[i].is_friend) {
					continue
				}
				res += Dashboard.profilesSkeleton(response[i])
			}
			res += '</div>'
			this.profilelistContainer.html(res)
		})
	}

	initfriends() {
        var response = Dashboard.send_xml_request('GET', this.friendlist_api)[0]
        if (response.length == 0) {
                return this.friendlistContainer.html(Dashboard.friendlistSkeleton())
        }
        var res = ''
        for (var i = response.length - 1; i >= 0; i--) {
                res += Dashboard.friendlistSkeleton(response[i])
        }
        this.friendlistContainer.html(res)
	}

	static friendlistSkeleton(row=null) {
		if (row==null) {
			return '<div class="col-sm-12 card-friends unavailable">Add Friends from available users</div>' 
		}
		var res = '<div class="col-sm-12 card-friends friendName" thread_id="' + row.thread_id + '" profile_name="' + row.username
		res += '"last_seen="' + row.last_active + '" onclick="_dash.initChatBox(this)">'
		var className = row.last_message_read ? '' : 'unread'
		res += '<p class="username ' + className + '">' + row.username + '<span class="online-info">' + Dashboard.online_attr(row) + '</span></p>'
		res += '<p class="lastmessage ' + className + '">' + row.last_thread_message + '</p>'
		res += '</div>' 
		return res
	}

	static online_attr(row) {
		if (row.is_online) {
			return '<i class="fa fa-circle online"></i>'
		}
		return '<i class="fa fa-circle offline"></i>'
	}

	static profilesSkeleton(row) {
		var res = '<div class="col-sm-3" id="parent_' + row.id +'">'
		res += '<div class="col-sm-12 card-profile"><img src="/static/images/no-avatar.png" /></div>'
		res += '<div class="col-sm-12 card-profile">' + row.username + '</div>'
		res += '<div class="col-sm-12 card-profile">'
		if (row.friend_request_send) {
			res += Dashboard.get_action('cancel', row.id, row.request_id)
		} else if (row.friend_request_recieved) {
			res += Dashboard.get_action('received,', row.id, row.request_id)
		} else {
			res += Dashboard.get_action('addFriend', row.id, row.request_id)
		}
		res += '</div></div>'
		return res
	}

	addFriend(that) {
		Dashboard.send_xml_request('POST', this.friendsrequest_api, JSON.stringify({
			'to_user': that.id
		}))
	}

	updateRequest(that) {
		Dashboard.send_xml_request('PATCH', this.updatefriendrequest_api + that.id + '/', JSON.stringify({
			'action': that.attributes.action.value
		}))
	}

	initChatBox(that) {
		Dashboard.openMessaageSocket(that.attributes.thread_id.value)
		$('.chatbox').show(200)
		$('#thread_input').val(that.attributes.thread_id.value)
		var inner_header = that.attributes.profile_name.value
		inner_header += ' 	<span style="font-size: 9px;"> ( Last seen: ' + that.attributes.last_seen.value + ')</span>'
		inner_header += '<i class="fa fa-times" onclick="Dashboard.close()"></i>'
		$('#profilename').html(inner_header)
		var response = Dashboard.send_xml_request('GET', this.message_api + that.attributes.thread_id.value)[0]
		var res = ''
		for (var i = response.length - 1; i >= 0; i--) {
			res += Dashboard.messageSkeleton(response[i], this.username)
		}
		this.chatContainer.html(res)
		this.chatContainer.scrollTop(this.chatContainer[0].scrollHeight)
	}

	sendMessage() {
		var data = {
			'text': $('#messagearea').val(),
			'thread': $('#thread_input').val()
		}
		var response = Dashboard.send_xml_request('POST', this.send_message_api, JSON.stringify(data))[0]
		$('#messagearea').val('')
	}

	static updateMessage(msg) {
		var data = JSON.parse(msg)
		_dash.chatContainer.append(Dashboard.messageSkeleton(data, _dash.username))
		_dash.chatContainer.scrollTop(_dash.chatContainer[0].scrollHeight)
	}

	static close() {
		$('.chatbox').hide(300)
		ws4redis_message.close()
	}

	static messageSkeleton(row, owner) {
		var className = row.username === owner ? 'right-chat' : 'left-chat'
		return '<p class="chatmessage ' + className + '">' + row.text + '<span class="chat-time">' + row.time + '</span></p>'
	}

	static get_action(action, id, request_id) {
		if (action === 'addFriend') {
			return '<p class="btn btn-default addFriend" id="' + id + '" onclick=_dash.addFriend(this)> + Add Friend</p>'
		} else if (action == 'cancel') {
			return '<p class="btn btn-default addFriend" id="' + request_id + '" action="cancel" action_id="'+id+'" onclick=_dash.updateRequest(this)>Cancel request</p>'
		} else {
			var resp = '<p><span class="btn btn-default accept" onclick="_dash.updateRequest(this)" action="accept" id="'+request_id+'">Accept</span>'
			resp += '<span class="btn btn-default reject" onclick="_dash.updateRequest(this)" action="reject" id="'+request_id+'">Reject</span>'
			return resp
		}
	}

	static updateFriendRequest(msg) {
		var data = JSON.parse(msg)
		if (data.is_friend) {
			$('#parent_' + data.id).remove()
		} else {
			$('#parent_' + data.id).replaceWith(Dashboard.profilesSkeleton(data))
		}
	}

	static updateFriendsInfo(msg) {
		var data = JSON.parse(msg)
		var res = ''
		for (var i = data.length - 1; i >= 0; i--) {
			res += Dashboard.friendlistSkeleton(data[i])
		}
		_dash.friendlistContainer.html(res)
	}

    static send_xml_request(method, api, data={}, sync=false, callback=null) {
        try {
            var xmlHttp = new XMLHttpRequest();
            xmlHttp.open( method, api, sync );
            if (callback != null && sync === true) {
                xmlHttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        callback()
                    }
                };
            }
            xmlHttp.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val())
            xmlHttp.setRequestHeader('Accept', 'application/json')
            xmlHttp.setRequestHeader('Content-Type', 'application/json')
            xmlHttp.send( data );
            return [JSON.parse(xmlHttp.responseText), xmlHttp.status]
        } catch(e) {
            alert('Something went wrong! Please Try Again')
            console.log(e)
        }
    }

    static openMessaageSocket(thread_id) {
        ws4redis_message = WS4Redis({
            uri: WEBSOCKET_URI + 'thread_' + thread_id + '?subscribe-broadcast',
            receive_message: Dashboard.updateMessage,
            heartbeat_msg: WS4REDIS_HEARTBEAT
        });
    }

    static openFriendSocket(profile_id) {
    	ws4redis_friend = WS4Redis({
            uri: WEBSOCKET_URI + 'update_friend_request_' + profile_id + '?subscribe-broadcast',
            receive_message: Dashboard.updateFriendRequest,
            heartbeat_msg: WS4REDIS_HEARTBEAT
        });
    }

    static receiveFriendSocket(profile_id) {
    	ws4redis_friendrequest_receive = WS4Redis({
            uri: WEBSOCKET_URI + 'friendrequestreceive_' + profile_id + '?subscribe-broadcast',
            receive_message: Dashboard.updateFriendRequest,
            heartbeat_msg: WS4REDIS_HEARTBEAT
        });
    }

    static updateFriendsDetails(profile_id) {
    	ws4redis_friends_online = WS4Redis({
            uri: WEBSOCKET_URI + 'friends_' + profile_id + '?subscribe-broadcast',
            receive_message: Dashboard.updateFriendsInfo,
            heartbeat_msg: WS4REDIS_HEARTBEAT
        });
    }
}