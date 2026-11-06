#include <algorithm>
#include <atomic>
#include <cmath>
#include <gz/plugin/Register.hh>
#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Link.hh>
#include <gz/sim/Util.hh>
#include <gz/sim/components/JointVelocityCmd.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/double.pb.h>

// A lumped pressure model, not a CFD solution. The seal only works near the
// x=0 wall, within its bounds, with the underside facing the wall.
class FanAdhesion : public gz::sim::System,
                    public gz::sim::ISystemConfigure,
                    public gz::sim::ISystemPreUpdate
{
  gz::sim::Entity base{gz::sim::kNullEntity};
  gz::sim::Entity rotor{gz::sim::kNullEntity};
  gz::transport::Node node;
  std::atomic<double> throttle{1.0};
public:
  void Configure(const gz::sim::Entity &entity,
                 const std::shared_ptr<const sdf::Element> &,
                 gz::sim::EntityComponentManager &ecm,
                 gz::sim::EventManager &) override
  {
    gz::sim::Model model(entity);
    base = model.LinkByName(ecm, "base_link");
    rotor = model.JointByName(ecm, "fan_joint");
    node.Subscribe("/fan_speed", &FanAdhesion::OnSpeed, this);
  }
  void OnSpeed(const gz::msgs::Double &msg)
  {
    if (std::isfinite(msg.data()))
      throttle.store(std::clamp(msg.data(), 0.0, 1.0));
  }
  void PreUpdate(const gz::sim::UpdateInfo &info,
                 gz::sim::EntityComponentManager &ecm) override
  {
    if (info.paused || base == gz::sim::kNullEntity) return;
    const double speed = throttle.load();
    if (rotor != gz::sim::kNullEntity)
      ecm.SetComponentData<gz::sim::components::JointVelocityCmd>(rotor, {200.0 * speed});
    const auto pose = gz::sim::worldPose(base, ecm);
    const auto normal = pose.Rot().RotateVector(gz::math::Vector3d(0, 0, -1));
    const auto pos = pose.Pos();
    // Chassis-to-wall standoff at wheel contact is 97 mm. Seal loss is
    // approximated linearly over the next 20 mm, and disappears off the wall.
    const double gap = -pos.X() - 0.097;
    if (gap < -0.015 || gap > 0.020 || normal.X() < 0.98 ||
        std::abs(pos.Y()) > 1.15 || pos.Z() < 0.35 || pos.Z() > 3.65) return;
    const double seal = std::clamp(1.0 - std::max(0.0, gap) / 0.020, 0.0, 1.0);
    // delta_p = 0.5 rho v^2 * efficiency; F = delta_p * effective area.
    const double pressure = 0.5 * 1.225 * std::pow(90.0 * speed, 2) * 0.8;
    const double force = pressure * 3.141592653589793 * 0.09 * 0.09 * seal;
    gz::sim::Link(base).AddWorldForce(ecm, normal * force);
  }
};
GZ_ADD_PLUGIN(FanAdhesion, gz::sim::System,
              FanAdhesion::ISystemConfigure, FanAdhesion::ISystemPreUpdate)
