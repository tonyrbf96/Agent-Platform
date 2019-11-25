import json

# definir bien la estructura de los mensajes acl
class ACLMessage:
    def __init__(self, data_json=None):
        if not data_json:
            self.data = {}
        else:
            self.data = json.loads(data_json)

    def get_msg(self):
        return json.dumps(self.data)

    @property
    def performative(self):
        "Gets the type of the communicative act of the ACL message"
        try:
            return self.data['performative']
        except KeyError:
            return None


    @performative.setter
    def performative(self, perform):
        "Sets the type of the communicative act of the ACL message"
        self.data['performative'] = perform


    @property
    def sender(self):
        "Gets the identity of the sender of the message, that is, the name of the agent of the communicative act."
        try:
            return self.data['sender']
        except KeyError:
            return None

    @sender.setter
    def sender(self, aid):
        "Sets the identity of the sender of the message"
        self.data['sender'] = aid


    def add_receiver(self, aid):
        "Denotes the identity of the intended recipients of the message"
        # Participant in communication
        try:
            self.data['receivers'].add(aid)
        except KeyError:
            self.data['receivers'] = [aid]

    def receivers(self, receivers):
        self.data[receivers]

    def get_all_receivers(self):
        "Gets all the receivers of the message"
        try:
            return self.data['receivers']
        except KeyError:
            return None

    
    def add_reply_to(self, aid):
        """This parameter indicates that subsequent messages in this conversation thread 
        are to be directed to the agent named in the reply-to parameter, instead of to 
        the agent named in the sender parameter."""
        # Participant in communication 
        try:
            self.data['reply-to'].add(aid)
        except KeyError:
            self.data['reply-to'] = [aid]


    def get_all_replies(self):
        """Get the list of all the agents that will receive the
        answer of the message"""
        try:
            return self.data['reply-to']
        except KeyError:
            return None

    
    @property
    def content(self):
        """ Denotes the content of the message; equivalently denotes the object of the action. 
        The meaning of the content of any ACL message is intended to be interpreted by the receiver 
        of the message. This is particularly relevant for instance when referring to referential 
        expressions, whose interpretation might be different for the sender and the receiver.
        """
        try:
            return self.data['content']
        except KeyError:
            return None

    @content.setter
    def content(self, content):
        "Sets the content parameter of the ACL message"
        self.data['content'] = content


    @property
    def language(self):
        "Denotes the language in which the content parameter is expressed"
        try:
            return self.data['language']
        except KeyError:
            return None

    @language.setter
    def language(self, lang):
        "Sets the language parameter of the ACL message"
        self.data['language'] = lang


    #? May be erased
    @property
    def ontology(self):
        "Denotes the ontology(s) used to give a meaning to the symbols in the content expression."
        try:
            return self.data['ontology']
        except KeyError:
            return None

    @ontology.setter
    def ontology(self, onto):
        "Sets the ontology parameter of the ACL message"
        self.data['ontology'] = onto


    # @property
    # def protocol(self):
    #     "Gets the protocol parameter of the ACL message"
    #     # Control of conversation
    #     pass

    # @protocol.setter
    # def protocol(self, protocol):
    #     "Sets the protocol parameter of the ACL message"
    #     pass

    @property
    def conversation_id(self):
        """Introduces an expression (a conversation identifier) which is used to identify 
        the ongoing sequence of communicative acts that together form a conversation.
        """
        try:
            return self.data['conversation-id']
        except KeyError:
            return None

    @conversation_id.setter
    def conversation_id(self, conv_id):
        "Sets the conversation-id parameter of the ACL message"
        return self.data['conversation-id']


    @property
    def reply_with(self):
        """Introduces an expression that will be used by the responding agent to identify this message.
        """
        try:
            return self.data['reply-with']
        except KeyError:
            return None

    @reply_with.setter
    def reply_with(self, reply_with):
        "Sets the reply-with parameter of the ACL message"
        self.data['reply-with'] = reply_with


    @property 
    def in_reply_with(self):
        "Denotes an expression that references an earlier action to which this message is a reply."
        try:
            return self.data['in-reply-with']
        except KeyError:
            return None

    @in_reply_with.setter
    def in_reply_with(self, in_reply_with):
        "Sets the in-reply-with parameter of the ACL message"
        self.data['in-reply-with'] = in_reply_with


    #? May be gone
    @property
    def reply_by(self):
        """Denotes a time and/or date expression which indicates the latest time by which 
        the sending agent would like to receive a reply."""
        try:
            return self.data['reply-by']
        except KeyError:
            return None

    @reply_by.setter
    def reply_by(self, value):
        self.data['reply-by'] = value


if __name__ == "__main__":
    data = {
        'performative': 'inform',
        'sender': {'name': 'i'},  
        'receiver': {'name': 'j'}, 
        'content': "weather (today, raining)",
        'language': 'Prolog'
    }
    msg = ACLMessage(json.dumps(data))
    print(msg.add_receiver({'name': 'k'}))
    print(msg.content)
        