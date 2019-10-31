
# definir bien la estructura de los mensajes acl
class ACLMessage:
    def __init__(self):
        pass


    @property
    def performative(self):
        "Gets the performative parameter of the ACL message"
        # Type of communicative acts
        pass

    @performative.setter
    def performative(self, performative):
        "Sets the performative parameter of the ACL message"
        pass

    @property
    def sender(self):
        "Gets the sender parameter of the ACL message"
        # Participant in communication
        pass

    @sender.setter
    def sender(self, aid):
        "Sets the agent that will send the message"
        pass

    def add_receiver(self, aid):
        "Adds the recipients for the message being created"
        # Participant in communication
        pass

    def get_all_receivers(self):
        "Gets all the receivers of the message"
        pass

    
    def add_reply_to(self, aid):
        """Used to add the agents that should receive the 
        answer of the message."""
        # Participant in communication 
        pass

    def get_all_replies(self):
        """Get the list of all the agents that will receive the
        answer of the message"""
        pass
    
    @property
    def content(self):
        "Gets the content parameter of the ACL message"
        # Content of message
        pass

    @content.setter
    def content(self, content):
        "Sets the content parameter of the ACL message"
        print('h')
        pass

    @property
    def language(self):
        "Gets the language parameter of the ACL message"
        # Description of Content
        pass

    @language.setter
    def language(self, lang):
        "Sets the language parameter of the ACL message"
        pass

    @property
    def encoding(self):
        "Gets the encoding parameter of the ACL message"
        # Description of Content
        pass

    @encoding.setter
    def encoding(self, encoding):
        "Sets the encoding parameter of the ACL message"
        pass

    @property
    def ontology(self):
        "Gets the ontology parameter of the ACL message"
        # Description of Content
        pass
    
    @antology.setter
    def ontology(self, ontology):
        "Sets the ontology parameter of the ACL message"
        pass

    @property
    def protocol(self):
        "Gets the protocol parameter of the ACL message"
        # Control of conversation
        pass

    @protocol.setter
    def protocol(self, protocol):
        "Sets the protocol parameter of the ACL message"
        pass

    @property
    def conversation_id(self):
        "Gets the conversation-id parameter of the ACL message"
        # Control of conversation
        pass

    @conversation_id.setter
    def conversation_id(self, conv_id):
        "Sets the conversation-id parameter of the ACL message"
        pass

    @property
    def reply_with(self):
        "Gets the reply-with parameter of the ACL message"
        # Control of conversation
        pass

    @reply_with.setter
    def reply_with(self, reply_with):
        "Sets the reply-with parameter of the ACL message"
        pass

    @property 
    def in_reply_with(self):
        "Gets the in-reply-with parameter of the ACL message"
        # Control of conversation
        pass

    @in_reply_with.setter
    def in_reply_with(self, in_reply_with):
        "Sets the in-reply-with parameter of the ACL message"
        pass

    @property
    def reply_by(self):
        "Gets the reply-by parameter of the ACL message"
        # Control of conversation
        pass

    @reply_by.setter
    def reply_with(self, reply_with):
        "Sets the reply-with parameter of the ACL message"
        pass