import 'package:flutter/material.dart';

void main() {
  runApp(const FlowEventsApp());
}

class FlowEventsApp extends StatelessWidget {
  const FlowEventsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Flow Events',
      theme: ThemeData(
        fontFamily: 'DM Sans',
        scaffoldBackgroundColor: const Color(0xFFF0F2F0),
      ),
      home: const ChatbotPage(),
    );
  }
}

class ChatbotPage extends StatefulWidget {
  const ChatbotPage({super.key});

  @override
  State<ChatbotPage> createState() => _ChatbotPageState();
}

class _ChatbotPageState extends State<ChatbotPage> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  bool isTyping = false;

  final List<Map<String, dynamic>> messages = [
    {
      "role": "assistant",
      "message":
          "¡Hola! Soy tu asistente de Flow Events ✨\nEstoy listo para ayudarte a organizar tu próximo evento.",
      "time": "09:30 AM"
    }
  ];

  void sendMessage([String? text]) async {
    final mensaje = text ?? _controller.text.trim();

    if (mensaje.isEmpty) return;

    setState(() {
      messages.add({
        "role": "user",
        "message": mensaje,
        "time": getTime(),
      });

      isTyping = true;
    });

    _controller.clear();

    scrollBottom();

    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      isTyping = false;

      messages.add({
        "role": "assistant",
        "message":
            "Perfecto ✨\nEstoy preparando ideas para tu evento \"$mensaje\".\n\nPodemos definir presupuesto, ciudad, invitados y proveedores.",
        "time": getTime(),
      });
    });

    scrollBottom();
  }

  void scrollBottom() {
    Future.delayed(const Duration(milliseconds: 300), () {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent + 200,
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeOut,
      );
    });
  }

  String getTime() {
    final now = TimeOfDay.now();
    final hour = now.hourOfPeriod == 0 ? 12 : now.hourOfPeriod;
    final minute = now.minute.toString().padLeft(2, '0');
    final period = now.period == DayPeriod.am ? 'AM' : 'PM';

    return "$hour:$minute $period";
  }

  Widget buildMessage(Map<String, dynamic> msg) {
    final isUser = msg["role"] == "user";

    return Padding(
      padding: const EdgeInsets.only(bottom: 22),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser)
            Container(
              width: 38,
              height: 38,
              margin: const EdgeInsets.only(right: 10),
              decoration: BoxDecoration(
                color: const Color(0xFF2ECC71),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(
                child: Text(
                  "✦",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

          Flexible(
            child: Column(
              crossAxisAlignment:
                  isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 14,
                  ),
                  decoration: BoxDecoration(
                    color: isUser
                        ? const Color(0xFF2563EB)
                        : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(18),
                      topRight: const Radius.circular(18),
                      bottomLeft:
                          Radius.circular(isUser ? 18 : 4),
                      bottomRight:
                          Radius.circular(isUser ? 4 : 18),
                    ),
                    boxShadow: isUser
                        ? []
                        : [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.05),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            )
                          ],
                  ),
                  child: Text(
                    msg["message"],
                    style: TextStyle(
                      color: isUser ? Colors.white : const Color(0xFF1A1A2E),
                      fontSize: 14.5,
                      height: 1.5,
                    ),
                  ),
                ),

                const SizedBox(height: 6),

                Text(
                  "${isUser ? 'Tú' : 'Flow AI'} • ${msg["time"]}",
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF6B7280),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildChip(String text, IconData icon) {
    return InkWell(
      onTap: () => sendMessage(text),
      borderRadius: BorderRadius.circular(30),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 10,
        ),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(
            color: const Color(0xFFE5E7EB),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16,
              color: const Color(0xFF6B7280),
            ),
            const SizedBox(width: 8),
            Text(
              text,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildTypingIndicator() {
    return Row(
      children: [
        Container(
          width: 38,
          height: 38,
          margin: const EdgeInsets.only(right: 10),
          decoration: BoxDecoration(
            color: const Color(0xFF2ECC71),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Center(
            child: Text(
              "✦",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),

        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: 18,
            vertical: 14,
          ),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
          ),
          child: Row(
            children: [
              buildDot(),
              buildDot(),
              buildDot(),
              const SizedBox(width: 10),
              const Text(
                "Escribiendo...",
                style: TextStyle(
                  color: Color(0xFF6B7280),
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget buildDot() {
    return Container(
      width: 7,
      height: 7,
      margin: const EdgeInsets.only(right: 5),
      decoration: const BoxDecoration(
        color: Color(0xFF2ECC71),
        shape: BoxShape.circle,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F0),

      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFFF0F2F0),
        centerTitle: false,
        titleSpacing: 20,
        title: Row(
          children: [
            Container(
              width: 34,
              height: 34,
              decoration: BoxDecoration(
                color: const Color(0xFF2ECC71),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Center(
                child: Text(
                  "✦",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            const SizedBox(width: 12),

            const Text(
              "Flow Events",
              style: TextStyle(
                color: Color(0xFF1A1A2E),
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),

        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 18),
            child: CircleAvatar(
              backgroundColor: const Color(0xFF2ECC71),
              child: const Text(
                "Y",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          )
        ],
      ),

      body: Column(
        children: [
          Expanded(
            child: ListView(
              controller: _scrollController,
              padding: const EdgeInsets.all(20),
              children: [
                ...messages.map(buildMessage),

                const SizedBox(height: 6),

                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    buildChip(
                      "Planificar Boda",
                      Icons.favorite,
                    ),
                    buildChip(
                      "Evento Corporativo",
                      Icons.business_center,
                    ),
                    buildChip(
                      "Cumpleaños",
                      Icons.cake,
                    ),
                    buildChip(
                      "Quinceañera",
                      Icons.star,
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                if (isTyping) buildTypingIndicator(),
              ],
            ),
          ),

          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 8, 18, 18),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.06),
                      blurRadius: 15,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () {},
                      icon: const Icon(
                        Icons.add_circle_outline,
                        color: Color(0xFF6B7280),
                      ),
                    ),

                    Expanded(
                      child: TextField(
                        controller: _controller,
                        minLines: 1,
                        maxLines: 5,
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                          hintText:
                              "Escribe el tipo de evento o una idea...",
                          hintStyle: TextStyle(
                            color: Color(0xFF6B7280),
                          ),
                        ),
                        onSubmitted: (_) => sendMessage(),
                      ),
                    ),

                    Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF2ECC71),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: IconButton(
                        onPressed: sendMessage,
                        icon: const Icon(
                          Icons.send,
                          color: Colors.white,
                        ),
                      ),
                    )
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}